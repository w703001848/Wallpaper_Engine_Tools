/** React renderer entrypoint for the media-library workspace. */
import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  AppWindow,
  Archive,
  Check,
  ChevronDown,
  ChevronRight,
  ChevronRight as ChevronExpand,
  Copy,
  Database,
  File as FileIcon,
  Film,
  FolderOpen,
  Globe,
  HardDrive,
  Image,
  Library,
  LoaderCircle,
  Play,
  RefreshCw,
  Search,
  Settings2,
  ShieldAlert,
  SlidersHorizontal,
  Terminal,
  Trash2,
  Upload,
  Video,
  X,
} from "lucide-react";
import type {
  AppSettings,
  ConflictAction,
  FilterState,
  FolderNode,
  NasArchivePlan,
  NasLocationStatus,
  NasMapping,
  OperationPlan,
  ProjectRecord,
  ProjectSource,
  ProjectType,
  RepkgOutputDirectory,
  StorageLogKind,
  TaskEvent,
} from "../shared/types.js";
import { formatFileSize } from "../shared/file-size.js";
import {
  displayFileName,
  isPreviewImage,
  isRepkgPackage,
} from "../shared/repkg-files.js";
import "./styles.css";
import "./extensions.css";
import "./setup.css";

const emptyFilter: FilterState = {
  search: "",
  sources: [],
  types: [],
  showInvalid: false,
  sort: "updatedAt",
  descending: true,
  page: 1,
  pageSize: 50,
  folderId: null,
};
type ProjectContextMenuState = {
  project: ProjectRecord;
  x: number;
  y: number;
};
const sourceLabels: Record<ProjectSource, string> = {
  workshop: "创意工坊",
  backup: "本地备份",
  temp: "临时目录",
  nas: "NAS",
  unknown: "未知",
};
const typeLabels: Record<ProjectType, string> = {
  scene: "场景",
  video: "视频",
  web: "网页",
  application: "应用",
  unknown: "其他",
};
const normalizeDescription = (value: string) =>
  value.replace(/\r\n/g, "\n").replace(/\\n/g, "\n").replace(/\/\/n/g, "\n");
const typeIcons: Record<ProjectType, typeof Image> = {
  scene: Image,
  video: Video,
  web: Globe,
  application: AppWindow,
  unknown: Film,
};
const titleFromPath = (value: string) => {
  const name = value.split(/[\\/]/).pop() || "";
  return name.replace(/\.[^.]+$/, "") || name;
};
// Steam metadata uses seconds while filesystem timestamps use milliseconds.
const formatDate = (value: number) => {
  const timestamp = value < 1_000_000_000_000 ? value * 1000 : value;
  const date = new Date(timestamp);
  return Number.isNaN(date.getTime())
    ? "未知"
    : date.toLocaleString("zh-CN", { dateStyle: "medium", timeStyle: "short" });
};

function App() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [filter, setFilter] = useState(emptyFilter);
  const [pageInput, setPageInput] = useState(String(emptyFilter.page));
  const [items, setItems] = useState<ProjectRecord[]>([]);
  const [folders, setFolders] = useState<FolderNode[]>([]);
  const [total, setTotal] = useState(0);
  const [selected, setSelected] = useState<ProjectRecord | null>(null);
  const [events, setEvents] = useState<TaskEvent[]>([]);
  const [tab, setTab] = useState<"library" | "repkg" | "storage" | "settings">(
    "library",
  );
  const [busy, setBusy] = useState(false);
  const [contextMenu, setContextMenu] =
    useState<ProjectContextMenuState | null>(null);
  const [contextActionBusy, setContextActionBusy] = useState(false);
  const [repkgPath, setRepkgPath] = useState("");
  const filterPreferencesReady = useRef(false);
  const load = async () => {
    const page = await window.remake.library.list({ filter });
    setItems(page.items);
    setTotal(page.total);
    if (selected) setSelected(await window.remake.library.get(selected.id));
  };
  useEffect(() => {
    // Load persisted folders on startup; they should not depend on a new scan event.
    void Promise.all([
      window.remake.settings.get(),
      window.remake.library.folders(),
    ]).then(([nextSettings, nextFolders]) => {
      setSettings(nextSettings);
      setFilter((current) => ({
        ...current,
        page: 1,
        pageSize: nextSettings.display.pageSize,
        ...nextSettings.libraryView,
      }));
      filterPreferencesReady.current = true;
      setFolders(nextFolders);
    });
    const off = window.remake.onTaskEvent((event) => {
      setEvents((old) =>
        [event, ...old.filter((item) => item.taskId !== event.taskId)].slice(
          0,
          8,
        ),
      );
      if (event.kind === "scan" && event.status === "completed") {
        void load();
        void window.remake.library.folders().then(setFolders);
      }
    });
    return off;
  }, []);
  useEffect(() => {
    if (settings) void load();
  }, [
    settings,
    filter.search,
    filter.page,
    filter.pageSize,
    filter.sort,
    filter.descending,
    filter.showInvalid,
    filter.folderId,
    filter.sources.join(","),
    filter.types.join(","),
  ]);
  useEffect(() => {
    setPageInput(String(filter.page));
  }, [filter.page]);
  useEffect(() => {
    if (!filterPreferencesReady.current) return;
    // View preferences are lightweight settings and must not trigger a source rescan or replace the current page.
    void window.remake.settings.update({
      libraryView: {
        sources: filter.sources,
        types: filter.types,
        sort: filter.sort,
        descending: filter.descending,
      },
    });
  }, [
    filter.sources.join(","),
    filter.types.join(","),
    filter.sort,
    filter.descending,
  ]);
  const pageCount = Math.max(1, Math.ceil(total / filter.pageSize));
  // All navigation paths are clamped because filtering can reduce the total while a later page is selected.
  const goToPage = (page: number) =>
    setFilter((current) => ({
      ...current,
      page: Math.min(pageCount, Math.max(1, page)),
    }));
  const commitPageInput = () => {
    const page = Number.parseInt(pageInput, 10);
    if (Number.isFinite(page)) goToPage(page);
    else setPageInput(String(filter.page));
  };
  useEffect(() => {
    if (filter.page > pageCount) goToPage(pageCount);
  }, [filter.page, pageCount]);
  const scan = async () => {
    setBusy(true);
    await window.remake.library.scan();
    setBusy(false);
  };
  // Saving a source setting invalidates cached rows immediately; rescan to populate the newly active roots.
  const updateSettings = async (patch: Partial<AppSettings>, rescan = true) => {
    const next = await window.remake.settings.update(patch);
    setSettings(next);
    setFilter((current) => ({
      ...current,
      page:
        patch.libraryView || current.pageSize !== next.display.pageSize
          ? 1
          : current.page,
      pageSize: next.display.pageSize,
      ...(patch.libraryView ? next.libraryView : {}),
    }));
    if (rescan) await scan();
  };
  const updateProject = (project: ProjectRecord, previousId = project.id) => {
    // IPC already persisted the record; mirror it into both React owners so cards and details stay consistent.
    setItems((current) =>
      current.map((item) => (item.id === previousId ? project : item)),
    );
    setSelected((current) => (current?.id === previousId ? project : current));
  };
  const archiveCompleted = async (project: ProjectRecord) => {
    // Storage-panel archives follow the same in-place update rule as the card context menu.
    updateProject(project, selected?.id ?? project.id);
  };
  const moveFromContextMenu = async (
    project: ProjectRecord,
    target: string,
    targetLabel: string,
    destination: "backup" | "temp",
  ) => {
    setContextMenu(null);
    setContextActionBusy(true);
    try {
      const plan = await window.remake.operations.preview({
        kind: "move",
        source: project.rootPath,
        target,
      });
      const failedChecks = Object.entries(plan.checks)
        .filter(([, passed]) => !passed)
        .map(([name]) => name);
      if (failedChecks.length) {
        alert(`无法转移：预检未通过（${failedChecks.join("、")}）`);
        return;
      }
      const conflictCopy = plan.conflicts.length
        ? "\n目标存在同名项目，将自动重命名。"
        : "";
      if (
        !confirm(
          `确认将“${project.title}”转移到${targetLabel}？\n${plan.target}${conflictCopy}`,
        )
      )
        return;
      const result = await window.remake.operations.execute(plan, {
        [plan.target]: plan.conflicts.length ? "rename" : "skip",
      });
      alert(result.message);
      if (result.success && result.changedPaths[0]) {
        const moved = await window.remake.library.relocateAfterMove(
          project.id,
          result.changedPaths[0],
          destination,
        );
        // Replace only this card so the active filters, sort order, category and page never reset.
        updateProject(moved);
      }
    } catch (error) {
      alert(error instanceof Error ? error.message : String(error));
    } finally {
      setContextActionBusy(false);
    }
  };
  const archiveFromContextMenu = async (
    project: ProjectRecord,
    mapping: NasMapping,
  ) => {
    setContextMenu(null);
    setContextActionBusy(true);
    try {
      const plan = await window.remake.storage.previewNasArchive(
        project.id,
        mapping.id,
      );
      const failedChecks = Object.entries(plan.checks)
        .filter(([, passed]) => !passed)
        .map(([name]) => name);
      if (failedChecks.length) {
        alert(`无法归档：预检未通过（${failedChecks.join("、")}）`);
        return;
      }
      const conflictCopy = plan.conflicts.length
        ? "\nNAS 中存在同名项目，将自动重命名。"
        : "";
      if (
        !confirm(
          `确认将“${project.title}”转移到 ${mapping.name}？\n本地备份目录会生成项目入口。${conflictCopy}`,
        )
      )
        return;
      const result = await window.remake.storage.executeNasArchive(
        plan,
        plan.conflicts.length ? "rename" : "skip",
      );
      alert(result.message);
      if (result.success && result.project)
        updateProject(result.project, project.id);
    } catch (error) {
      alert(error instanceof Error ? error.message : String(error));
    } finally {
      setContextActionBusy(false);
    }
  };
  const toggle = <T extends string>(
    value: T,
    values: T[],
    setter: (value: T[]) => void,
  ) =>
    setter(
      values.includes(value)
        ? values.filter((item) => item !== value)
        : [...values, value],
    );
  if (!settings)
    return (
      <div className="loading">
        <LoaderCircle className="spin" />
        正在准备工作区…
      </div>
    );
  if (!settings.steamPath && !settings.wallpaperPath)
    return <SetupWizard onDone={setSettings} />;
  return (
    <div className="app-shell">
      <main
        className={
          tab === "library" ? "workspace library-workspace" : "workspace"
        }
      >
        <header className="topbar">
          <div className="title-block">
            <div className="brand">
              <div className="brand-mark">W</div>
              <div>
                <p className="eyebrow">WALLPAPER ENGINE TOOLS</p>
                <div>壁纸库管理</div>
              </div>
            </div>
          </div>
          <nav className="top-nav" aria-label="主菜单">
            {[
              ["library", Library, "壁纸库"],
              ["repkg", Archive, "RePKG 提取"],
              ["storage", HardDrive, "存储整理"],
              ["settings", Settings2, "设置"],
            ].map(([key, Icon, label]) => (
              <button
                className={tab === key ? "nav-item active" : "nav-item"}
                onClick={() => setTab(key as typeof tab)}
                key={key as string}
              >
                <Icon size={17} />
                {label as string}
              </button>
            ))}
          </nav>
          <div className="top-actions">
            {tab === "library" && (
              <section className="toolbar">
                <div className="search">
                  <Search size={17} />
                  <input
                    value={filter.search}
                    placeholder="搜索标题、ID 或描述"
                    onChange={(e) =>
                      setFilter({ ...filter, search: e.target.value, page: 1 })
                    }
                  />
                </div>
                <select
                  value={filter.sort}
                  onChange={(e) =>
                    setFilter({
                      ...filter,
                      sort: e.target.value as FilterState["sort"],
                    })
                  }
                >
                  <option value="updatedAt">最近更新</option>
                  <option value="title">名称</option>
                  <option value="fileSize">文件大小</option>
                  <option value="subscriptionDate">订阅日期</option>
                </select>
                <button
                  className={filter.descending ? "chip active" : "chip"}
                  onClick={() =>
                    setFilter({ ...filter, descending: !filter.descending })
                  }
                >
                  {filter.descending ? "倒序" : "正序"}
                </button>
                <button
                  className={filter.showInvalid ? "chip active" : "chip"}
                  onClick={() =>
                    setFilter({
                      ...filter,
                      showInvalid: !filter.showInvalid,
                      page: 1,
                    })
                  }
                >
                  <ShieldAlert size={14} />
                  失效
                </button>
                <button
                  className="ghost-button"
                  onClick={() => void scan()}
                  disabled={busy}
                >
                  <RefreshCw size={16} className={busy ? "spin" : ""} />
                  {busy ? "扫描中" : "重新扫描"}
                </button>
              </section>
            )}
            <button
              className="icon-button"
              title="诊断"
              onClick={async () =>
                alert(
                  JSON.stringify(
                    await window.remake.diagnostics.getEnvironment(),
                    null,
                    2,
                  ),
                )
              }
            >
              <Terminal size={17} />
            </button>
          </div>
        </header>
        {tab === "library" && (
          <div className="library-view">
            <div className="content-grid">
              <aside className="filters">
                <FilterSection title="来源">
                  <FilterChecks
                    values={["workshop", "backup", "temp", "nas"]}
                    selected={filter.sources}
                    labels={sourceLabels}
                    onToggle={(v) =>
                      toggle(v, filter.sources, (sources) =>
                        setFilter({ ...filter, sources, page: 1 }),
                      )
                    }
                  />
                </FilterSection>
                <FilterSection title="类型">
                  <FilterChecks
                    values={["scene", "video", "web", "application"]}
                    selected={filter.types}
                    labels={typeLabels}
                    onToggle={(v) =>
                      toggle(v, filter.types, (types) =>
                        setFilter({ ...filter, types, page: 1 }),
                      )
                    }
                  />
                </FilterSection>
                {folders.length > 0 && (
                  <FilterSection title="分类">
                    <FolderTree
                      nodes={folders}
                      selected={filter.folderId}
                      onSelect={(folderId) =>
                        setFilter({ ...filter, folderId, page: 1 })
                      }
                    />
                  </FilterSection>
                )}
                <div className="filter-note">
                  <SlidersHorizontal size={16} />
                  <span>共 {total} 个项目</span>
                </div>
              </aside>
              <section className="library-area">
                <div className="section-meta">
                  <span>
                    {total
                      ? `${(filter.page - 1) * filter.pageSize + 1}-${Math.min(filter.page * filter.pageSize, total)} / ${total}`
                      : "暂无索引"}
                  </span>
                  <button
                    className="text-button"
                    onClick={() => setFilter(emptyFilter)}
                  >
                    重置筛选
                  </button>
                </div>
                <div
                  className="card-grid"
                  style={
                    {
                      "--library-column-width": `calc((100% - ${(settings.display.columnCount - 1) * 13}px) / ${settings.display.columnCount})`,
                    } as React.CSSProperties
                  }
                >
                  {items.map((item) => (
                    <ProjectCard
                      key={item.id}
                      item={item}
                      selected={selected?.id === item.id}
                      onClick={() => setSelected(item)}
                      onContextMenu={(event) => {
                        event.preventDefault();
                        setSelected(item);
                        // Keep the fixed menu inside the viewport even near the bottom-right corner.
                        setContextMenu({
                          project: item,
                          x: Math.min(event.clientX, window.innerWidth - 300),
                          y: Math.min(event.clientY, window.innerHeight - 360),
                        });
                      }}
                    />
                  ))}
                  {!items.length && (
                    <div className="empty-state">
                      <Database size={34} />
                      <strong>还没有索引项目</strong>
                      <span>
                        在设置中配置目录后，点击“重新扫描”开始建立媒体库。
                      </span>
                    </div>
                  )}
                </div>
                <div className="pagination">
                  <button
                    className="page-control"
                    disabled={filter.page <= 1}
                    onClick={() => goToPage(1)}
                  >
                    第一页
                  </button>
                  <button
                    className="page-control"
                    disabled={filter.page <= 1}
                    onClick={() => goToPage(filter.page - 1)}
                  >
                    上一页
                  </button>
                  <label className="page-jump">
                    <span>第</span>
                    <input
                      aria-label="跳转页码"
                      inputMode="numeric"
                      value={pageInput}
                      onChange={(event) =>
                        setPageInput(event.target.value.replace(/\D/g, ""))
                      }
                      onKeyDown={(event) => {
                        if (event.key === "Enter") commitPageInput();
                      }}
                      onBlur={commitPageInput}
                    />
                    <span>页 / {pageCount}</span>
                  </label>
                  <button
                    className="page-control"
                    disabled={filter.page >= pageCount}
                    onClick={() => goToPage(filter.page + 1)}
                  >
                    下一页
                  </button>
                  <button
                    className="page-control"
                    disabled={filter.page >= pageCount}
                    onClick={() => goToPage(pageCount)}
                  >
                    最后一页
                  </button>
                </div>
              </section>
              <Details
                item={selected}
                onClose={() => setSelected(null)}
                onProjectUpdated={updateProject}
              />
            </div>
          </div>
        )}
        {tab === "repkg" && (
          <RepkgPanel path={repkgPath} setPath={setRepkgPath} events={events} />
        )}
        {tab === "storage" && (
          <StoragePanel
            settings={settings}
            selected={selected}
            onArchived={archiveCompleted}
            events={events}
          />
        )}
        {tab === "settings" && (
          <SettingsPanel settings={settings} updateSettings={updateSettings} />
        )}
        {contextMenu && (
          <ProjectContextMenu
            state={contextMenu}
            settings={settings}
            busy={contextActionBusy}
            onClose={() => setContextMenu(null)}
            onMove={moveFromContextMenu}
            onArchive={archiveFromContextMenu}
          />
        )}
      </main>
    </div>
  );
}

function SetupWizard({ onDone }: { onDone: (settings: AppSettings) => void }) {
  const [steam, setSteam] = useState("");
  const [wallpaper, setWallpaper] = useState("");
  const [backup, setBackup] = useState("");
  const detect = async () => {
    const found = await window.remake.settings.detectPaths();
    setSteam(found.steamPath || "");
    setWallpaper(found.wallpaperPath || "");
    setBackup(found.backupPath || "");
  };
  const finish = async () =>
    onDone(
      await window.remake.settings.update({
        steamPath: steam,
        wallpaperPath: wallpaper,
        backupPath: backup,
      }),
    );
  return (
    <main className="setup">
      <div className="setup-panel">
        <div className="brand-mark">W</div>
        <p className="eyebrow">首次设置</p>
        <h1>连接你的壁纸库</h1>
        <p className="setup-copy">
          配置只保存在重制版用户数据目录，旧版文件不会被读取或覆盖。
        </p>
        <button
          className="ghost-button detect-button"
          onClick={() => void detect()}
        >
          <RefreshCw size={15} />
          自动识别本机路径
        </button>
        <label>
          Steam 目录
          <input value={steam} onChange={(e) => setSteam(e.target.value)} />
        </label>
        <label>
          Wallpaper Engine 目录
          <input
            value={wallpaper}
            onChange={(e) => setWallpaper(e.target.value)}
          />
        </label>
        <label>
          我的壁纸目录
          <input value={backup} onChange={(e) => setBackup(e.target.value)} />
        </label>
        <button
          className="primary-button setup-finish"
          disabled={!steam && !wallpaper}
          onClick={() => void finish()}
        >
          进入壁纸库
          <ChevronRight size={16} />
        </button>
      </div>
    </main>
  );
}

function FilterSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="filter-section">
      <h3>{title}</h3>
      {children}
    </section>
  );
}
function FilterChecks<T extends string>({
  values,
  selected,
  labels,
  onToggle,
}: {
  values: T[];
  selected: T[];
  labels: Record<T, string>;
  onToggle: (value: T) => void;
}) {
  return (
    <div className="check-list">
      {values.map((value) => (
        <button
          className={
            selected.includes(value) ? "check-row checked" : "check-row"
          }
          key={value}
          onClick={() => onToggle(value)}
        >
          <span className="check-box">
            {selected.includes(value) && <Check size={12} />}
          </span>
          {labels[value]}
        </button>
      ))}
    </div>
  );
}
function FolderTree({
  nodes,
  selected,
  onSelect,
}: {
  nodes: FolderNode[];
  selected: string | null;
  onSelect: (id: string | null) => void;
}) {
  const [collapsed, setCollapsed] = useState<Set<string>>(() => new Set());
  const toggleNode = (id: string) =>
    setCollapsed((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const renderNodes = (items: FolderNode[], depth: number): React.ReactNode =>
    items.map((node) => {
      const hasChildren = node.children.length > 0;
      const isCollapsed = collapsed.has(node.id);
      return (
        <React.Fragment key={node.id}>
          <div className="folder-row-wrap" style={{ paddingLeft: depth * 12 }}>
            <button
              className="folder-toggle"
              type="button"
              disabled={!hasChildren}
              aria-label={
                hasChildren
                  ? `${isCollapsed ? "展开" : "折叠"} ${node.title}`
                  : undefined
              }
              title={
                hasChildren
                  ? `${isCollapsed ? "展开" : "折叠"} ${node.title}`
                  : undefined
              }
              onClick={() => hasChildren && toggleNode(node.id)}
            >
              {hasChildren ? (
                isCollapsed ? (
                  <ChevronExpand size={13} />
                ) : (
                  <ChevronDown size={13} />
                )
              ) : (
                <span className="folder-toggle-placeholder" />
              )}
            </button>
            <button
              className={
                selected === node.id ? "folder-row active" : "folder-row"
              }
              onClick={() => onSelect(node.id)}
            >
              {node.title}
            </button>
          </div>
          {hasChildren && !isCollapsed && renderNodes(node.children, depth + 1)}
        </React.Fragment>
      );
    });
  return (
    <div className="folder-tree">
      <button
        className={
          !selected ? "folder-row root-folder" : "folder-row root-folder active"
        }
        onClick={() => onSelect(null)}
      >
        全部分类
      </button>
      {renderNodes(nodes, 0)}
    </div>
  );
}
function Thumbnail({
  path: previewPath,
  size = 24,
}: {
  path: string | null;
  size?: number;
}) {
  const [source, setSource] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    setSource(null);
    if (previewPath)
      void window.remake.library.getThumbnail(previewPath).then((value) => {
        if (active) setSource(value);
      });
    return () => {
      active = false;
    };
  }, [previewPath]);
  return source ? (
    <img src={source} />
  ) : (
    <div className="thumb-placeholder">
      <Library size={size} />
    </div>
  );
}
function ProjectCard({
  item,
  selected,
  onClick,
  onContextMenu,
}: {
  item: ProjectRecord;
  selected: boolean;
  onClick: () => void;
  onContextMenu: (event: React.MouseEvent<HTMLButtonElement>) => void;
}) {
  const TypeIcon = typeIcons[item.type];
  return (
    <button
      className={selected ? "project-card selected" : "project-card"}
      onClick={onClick}
      onContextMenu={onContextMenu}
    >
      <div className="thumb">
        <Thumbnail path={item.previewPath} />
        <div
          className={`project-tag source-${item.source}`}
          title={`${sourceLabels[item.source]} · ${typeLabels[item.type]} · ${formatFileSize(item.fileSize)}`}
        >
          <TypeIcon size={13} />
          <span>{formatFileSize(item.fileSize)}</span>
        </div>
        <strong className="card-title-overlay" title={item.title}>
          {item.title}
        </strong>
        {item.invalid && <span className="invalid-badge">失效</span>}
      </div>
    </button>
  );
}
function ProjectContextMenu({
  state,
  settings,
  busy,
  onClose,
  onMove,
  onArchive,
}: {
  state: ProjectContextMenuState;
  settings: AppSettings;
  busy: boolean;
  onClose: () => void;
  onMove: (
    project: ProjectRecord,
    target: string,
    targetLabel: string,
    destination: "backup" | "temp",
  ) => Promise<void>;
  onArchive: (project: ProjectRecord, mapping: NasMapping) => Promise<void>;
}) {
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", closeOnEscape);
    window.addEventListener("blur", onClose);
    return () => {
      window.removeEventListener("keydown", closeOnEscape);
      window.removeEventListener("blur", onClose);
    };
  }, [onClose]);
  const pathKey = (value: string) =>
    value.replaceAll("/", "\\").replace(/\\+$/u, "").toLocaleLowerCase();
  const parentPath = state.project.rootPath.replace(/[\\/][^\\/]+[\\/]?$/u, "");
  const alreadyIn = (target: string) => pathKey(parentPath) === pathKey(target);
  const canArchive =
    Boolean(settings.backupPath) &&
    !state.project.storagePath &&
    ["workshop", "backup", "temp"].includes(state.project.source);
  return (
    <div className="context-menu-layer" onMouseDown={onClose}>
      <div
        className="project-context-menu"
        style={{ left: state.x, top: state.y }}
        role="menu"
        aria-label={`${state.project.title} 操作菜单`}
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="context-menu-title" title={state.project.title}>
          {state.project.title}
        </div>
        <div className="context-menu-group context-menu-commands">
          <button
            role="menuitem"
            onClick={() => {
              onClose();
              void window.remake.library.copyText(state.project.title);
            }}
          >
            <Copy size={15} />
            <span>复制标题</span>
          </button>
          <button
            role="menuitem"
            onClick={() => {
              onClose();
              void window.remake.library.openPath(state.project.rootPath);
            }}
          >
            <FolderOpen size={15} />
            <span>打开目录</span>
          </button>
        </div>
        <div className="context-menu-group">
          <span>转移到本地目录</span>
          <button
            role="menuitem"
            disabled={
              busy || !settings.backupPath || alreadyIn(settings.backupPath)
            }
            onClick={() =>
              void onMove(
                state.project,
                settings.backupPath,
                "备份目录",
                "backup",
              )
            }
          >
            <Archive size={15} />
            <span>备份目录</span>
          </button>
          {settings.tempDirectories
            .filter((directory) => directory.enabled)
            .map((directory) => (
              <button
                role="menuitem"
                key={directory.id}
                disabled={busy || alreadyIn(directory.path)}
                onClick={() =>
                  void onMove(
                    state.project,
                    directory.path,
                    `临时目录“${directory.name}”`,
                    "temp",
                  )
                }
              >
                <FolderOpen size={15} />
                <span>{directory.name}</span>
              </button>
            ))}
          {!settings.tempDirectories.some((directory) => directory.enabled) && (
            <div className="context-menu-empty">未配置临时目录</div>
          )}
        </div>
        <div className="context-menu-group">
          <span>转移到 NAS</span>
          {settings.nasMappings
            .filter((mapping) => mapping.enabled)
            .map((mapping) => (
              <button
                role="menuitem"
                key={mapping.id}
                disabled={busy || !canArchive}
                onClick={() => void onArchive(state.project, mapping)}
              >
                <HardDrive size={15} />
                <span>{mapping.name}</span>
              </button>
            ))}
          {!settings.nasMappings.some((mapping) => mapping.enabled) && (
            <div className="context-menu-empty">未配置 NAS 位置</div>
          )}
        </div>
      </div>
    </div>
  );
}
function Details({
  item,
  onClose,
  onProjectUpdated,
}: {
  item: ProjectRecord | null;
  onClose: () => void;
  onProjectUpdated: (project: ProjectRecord) => void;
}) {
  const [title, setTitle] = useState(item?.title || "");
  const [description, setDescription] = useState(() =>
    normalizeDescription(item?.description || ""),
  );
  const [size, setSize] = useState(item?.fileSize || 0);
  const [sizeError, setSizeError] = useState("");
  useEffect(() => {
    setTitle(item?.title || "");
    setDescription(normalizeDescription(item?.description || ""));
    setSizeError("");
  }, [item?.id]);
  useEffect(() => {
    setSize(item?.fileSize || 0);
  }, [item?.fileSize]);
  if (!item)
    return (
      <aside className="details empty-details">
        <FolderOpen size={28} />
        <span>选择一个项目查看详情</span>
      </aside>
    );
  const save = async () => {
    const project = await window.remake.library.updateMetadata(item.id, {
      title,
      description,
      favorite: item.favorite,
      tags: item.tags,
    });
    onProjectUpdated(project);
    alert("项目元数据已保存");
  };
  const recalculate = async () => {
    setSizeError("");
    try {
      const project = await window.remake.library.recalculateSize(item.id);
      setSize(project.fileSize);
      onProjectUpdated(project);
    } catch (error) {
      setSizeError(error instanceof Error ? error.message : String(error));
    }
  };
  return (
    <aside className="details">
      <div className="details-head">
        <span>项目详情</span>
        <button className="icon-button" onClick={onClose}>
          <X size={16} />
        </button>
      </div>
      <div className="detail-preview">
        <Thumbnail path={item.previewPath} size={32} />
      </div>
      <label>
        标题
        <input value={title} onChange={(e) => setTitle(e.target.value)} />
      </label>
      <label>
        描述
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={6}
        />
      </label>
      <div className="detail-tags">
        <span>{sourceLabels[item.source]}</span>
        <span>{typeLabels[item.type]}</span>
        <span>{formatFileSize(size)}</span>
      </div>
      <dl className="detail-meta">
        <div>
          <dt>最近更新</dt>
          <dd>{formatDate(item.updatedAt)}</dd>
        </div>
        <div>
          <dt>订阅时间</dt>
          <dd>{formatDate(item.subscriptionDate)}</dd>
        </div>
      </dl>
      <div className="detail-actions">
        <button className="primary-button" onClick={() => void save()}>
          <Check size={15} />
          {item.missingProject ? "生成 project.json" : "保存修改"}
        </button>
        <button
          className="ghost-button"
          onClick={() => void navigator.clipboard.writeText(item.title)}
        >
          复制标题
        </button>
        <button className="ghost-button" onClick={() => void recalculate()}>
          <RefreshCw size={15} />
          重新计算容量
        </button>
        {sizeError && (
          <div className="repkg-error" role="alert">
            {sizeError}
          </div>
        )}
        <button
          className="ghost-button"
          onClick={() => void window.remake.library.openPath(item.rootPath)}
        >
          <FolderOpen size={15} />
          打开目录
        </button>
      </div>
    </aside>
  );
}
function RepkgImage({ file }: { file: string }) {
  const [source, setSource] = useState<string | null | undefined>();
  const name = displayFileName(file);
  useEffect(() => {
    let active = true;
    setSource(undefined);
    void window.remake.library.getThumbnail(file).then((value) => {
      if (active) setSource(value);
    });
    return () => {
      active = false;
    };
  }, [file]);
  return (
    <figure className="repkg-image">
      <button
        className="repkg-image-frame"
        type="button"
        title="打开图片"
        onClick={() => void window.remake.library.openPath(file)}
      >
        {source ? (
          <img src={source} alt={name} />
        ) : source === undefined ? (
          <span>
            <LoaderCircle className="spin" size={24} />
            正在加载图片
          </span>
        ) : (
          <span>无法预览图片</span>
        )}
      </button>
      <figcaption title={file}>{name}</figcaption>
    </figure>
  );
}
function RepkgOutputList({ files }: { files: string[] }) {
  return (
    <div className="output-list">
      {files.map((file) =>
        isPreviewImage(file) ? (
          <RepkgImage file={file} key={file} />
        ) : (
          <button
            className="file-result"
            key={file}
            title={file}
            onClick={() => void window.remake.library.openPath(file)}
          >
            <FileIcon size={15} />
            {displayFileName(file)}
          </button>
        ),
      )}
    </div>
  );
}
function RepkgHistory({
  entries,
  currentJobId,
  onDeleted,
}: {
  entries: RepkgOutputDirectory[];
  currentJobId: string | null;
  onDeleted: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState<Set<string>>(() => new Set());
  const [outputs, setOutputs] = useState<Record<string, string[]>>({});
  const visible = entries.filter((entry) => entry.id !== currentJobId);
  const toggle = async (entry: RepkgOutputDirectory) => {
    if (expanded.has(entry.id)) {
      setExpanded((current) => {
        const next = new Set(current);
        next.delete(entry.id);
        return next;
      });
      return;
    }
    setExpanded((current) => new Set(current).add(entry.id));
    if (!(entry.id in outputs)) {
      const files = await window.remake.repkg.getOutput(entry.id);
      setOutputs((current) => ({ ...current, [entry.id]: files }));
    }
  };
  const remove = async (entry: RepkgOutputDirectory) => {
    if (!confirm(`确认永久删除此历史导出目录？\n${entry.outputPath}`)) return;
    try {
      if (!(await window.remake.repkg.deleteOutput(entry.id))) {
        alert("目录不存在或无法删除");
        return;
      }
      setExpanded((current) => {
        const next = new Set(current);
        next.delete(entry.id);
        return next;
      });
      setOutputs((current) => {
        const next = { ...current };
        delete next[entry.id];
        return next;
      });
      onDeleted(entry.id);
    } catch (removeError) {
      alert(
        removeError instanceof Error
          ? removeError.message
          : String(removeError),
      );
    }
  };
  if (!visible.length) return null;
  return (
    <section className="repkg-history">
      <div className="repkg-history-title">
        <h3>历史导出文件夹</h3>
        <span>{visible.length}</span>
      </div>
      <div className="repkg-history-entry">
        {visible.map((entry) => {
          const isExpanded = expanded.has(entry.id);
          const files = outputs[entry.id];
          return (
            <article className="repkg-history-item" key={entry.id}>
              <div className="repkg-history-row">
                <button
                  className="folder-toggle"
                  type="button"
                  title={isExpanded ? "收起文件" : "展开文件"}
                  aria-label={isExpanded ? "收起文件" : "展开文件"}
                  onClick={() => void toggle(entry)}
                >
                  {isExpanded ? (
                    <ChevronDown size={15} />
                  ) : (
                    <ChevronExpand size={15} />
                  )}
                </button>
                <div>
                  <code title={entry.outputPath}>{entry.outputPath}</code>
                  <time>{formatDate(entry.updatedAt)}</time>
                </div>
                <button
                  className="icon-button"
                  type="button"
                  title="打开导出目录"
                  aria-label="打开导出目录"
                  onClick={() =>
                    void window.remake.library.openPath(entry.outputPath)
                  }
                >
                  <FolderOpen size={16} />
                </button>
                <button
                  className="icon-button repkg-delete-button"
                  type="button"
                  title="永久删除历史导出"
                  aria-label="永久删除历史导出"
                  onClick={() => void remove(entry)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
              {isExpanded && (
                <div className="repkg-history-output">
                  {files ? (
                    files.length ? (
                      <RepkgOutputList files={files} />
                    ) : (
                      <span>目录中没有文件</span>
                    )
                  ) : (
                    <span>
                      <LoaderCircle className="spin" size={14} />
                      正在读取文件
                    </span>
                  )}
                </div>
              )}
            </article>
          );
        })}
      </div>
    </section>
  );
}
function RepkgPanel({
  path: inputPath,
  setPath,
  events,
}: {
  path: string;
  setPath: (v: string) => void;
  events: TaskEvent[];
}) {
  const [jobId, setJobId] = useState<string | null>(null);
  const [outputPath, setOutputPath] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [history, setHistory] = useState<RepkgOutputDirectory[]>([]);
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState("");
  const dragDepth = useRef(0);
  const event = events.find((item) => item.taskId === jobId);
  const acceptPath = (filePath: string) => {
    if (!isRepkgPackage(filePath)) {
      setError("仅支持 .pkg 或 .mpkg 文件");
      return false;
    }
    setPath(filePath);
    setError("");
    return true;
  };
  const loadHistory = async () =>
    setHistory(await window.remake.repkg.listHistory());
  const run = async () => {
    if (!acceptPath(inputPath)) return;
    setFiles([]);
    const next = await window.remake.repkg.start(inputPath);
    setJobId(next.id);
    setOutputPath(next.outputPath);
    await loadHistory();
  };
  const choose = async () => {
    const file = await window.remake.settings.pickFile([
      { name: "RePKG", extensions: ["pkg", "mpkg"] },
    ]);
    if (file) acceptPath(file);
  };
  const refresh = async () => {
    if (jobId) setFiles(await window.remake.repkg.getOutput(jobId));
  };
  useEffect(() => {
    void loadHistory();
  }, []);
  useEffect(() => {
    if (event?.status === "completed") {
      void refresh();
      void loadHistory();
    }
  }, [event?.status, jobId]);
  const drop = (dragEvent: React.DragEvent<HTMLElement>) => {
    dragEvent.preventDefault();
    dragDepth.current = 0;
    setDragging(false);
    const file = Array.from(dragEvent.dataTransfer.files).find((item) =>
      isRepkgPackage(item.name),
    );
    if (!file) {
      setError("拖入内容中没有 .pkg 或 .mpkg 文件");
      return;
    }
    acceptPath(window.remake.repkg.getPathForFile(file));
  };
  return (
    <section
      className="tool-panel repkg-panel"
      onDragEnter={(dragEvent) => {
        dragEvent.preventDefault();
        dragDepth.current += 1;
        setDragging(true);
      }}
      onDragOver={(dragEvent) => {
        dragEvent.preventDefault();
        dragEvent.dataTransfer.dropEffect = "copy";
      }}
      onDragLeave={() => {
        dragDepth.current = Math.max(0, dragDepth.current - 1);
        if (dragDepth.current === 0) setDragging(false);
      }}
      onDrop={drop}
    >
      <div className="panel-intro">
        <Archive size={20} />
        <div>
          <h2>纹理提取</h2>
          <p>每个任务使用独立目录，历史结果保留 7 天后自动清理。</p>
        </div>
      </div>
      <div
        className={dragging ? "repkg-drop-zone dragging" : "repkg-drop-zone"}
      >
        <div className="repkg-drop-copy">
          <Upload size={18} />
          <span>{dragging ? "释放文件以识别" : "拖入 .pkg 或 .mpkg 文件"}</span>
        </div>
        <div className="path-row">
          <input
            value={inputPath}
            onChange={(changeEvent) => {
              setPath(changeEvent.target.value);
              setError("");
            }}
            placeholder="选择 .pkg 或 .mpkg 文件"
          />
          <button className="ghost-button" onClick={() => void choose()}>
            <FolderOpen size={15} />
            选择
          </button>
          <button
            className="primary-button"
            onClick={() => void run()}
            disabled={!inputPath}
          >
            <Play size={15} />
            开始提取
          </button>
        </div>
        {error && (
          <div className="repkg-error" role="alert">
            {error}
          </div>
        )}
      </div>
      {jobId && (
        <div className="job-card">
          <div className="job-line">
            <span>{event?.status || "正在启动"}</span>
            <div>
              <button className="text-button" onClick={() => void refresh()}>
                刷新结果
              </button>
              {event?.status === "running" && (
                <button
                  className="text-button danger"
                  onClick={() => void window.remake.repkg.cancel(jobId)}
                >
                  取消
                </button>
              )}
            </div>
          </div>
          {outputPath && (
            <div className="repkg-output-directory">
              <div>
                <span>导出目录</span>
                <code title={outputPath}>{outputPath}</code>
              </div>
              <button
                className="icon-button"
                type="button"
                title="打开导出目录"
                aria-label="打开导出目录"
                onClick={() => void window.remake.library.openPath(outputPath)}
              >
                <FolderOpen size={16} />
              </button>
            </div>
          )}
          <div className="progress">
            <i style={{ width: `${event?.progress || 0}%` }} />
          </div>
          {files.length > 0 && <RepkgOutputList files={files} />}
        </div>
      )}
      <RepkgHistory
        entries={history}
        currentJobId={jobId}
        onDeleted={(id) =>
          setHistory((current) => current.filter((entry) => entry.id !== id))
        }
      />
      <TaskLog events={events.filter((item) => item.kind === "repkg")} />
    </section>
  );
}
function NasLocationSettings({
  settings,
  updateSettings,
}: {
  settings: AppSettings;
  updateSettings: (
    patch: Partial<AppSettings>,
    rescan?: boolean,
  ) => Promise<void>;
}) {
  const [statuses, setStatuses] = useState<NasLocationStatus[]>([]);
  const [editing, setEditing] = useState<NasMapping | null>(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const statusFor = (id: string) =>
    statuses.find((item) => item.mappingId === id);
  const refresh = async () => {
    setBusy(true);
    try {
      setStatuses(await window.remake.storage.checkNasLocations());
    } finally {
      setBusy(false);
    }
  };
  // Location health is checked when Settings opens and after each configuration change; no background polling is needed.
  useEffect(() => {
    void refresh();
  }, []);
  const saveMapping = async () => {
    if (!editing) return;
    setMessage("");
    try {
      const exists = settings.nasMappings.some(
        (item) => item.id === editing.id,
      );
      const nasMappings = exists
        ? settings.nasMappings.map((item) =>
            item.id === editing.id ? editing : item,
          )
        : [...settings.nasMappings, editing];
      // NAS mappings are archive targets, so editing them must not trigger a library rescan.
      await updateSettings({ nasMappings }, false);
      setEditing(null);
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    }
  };
  const removeMapping = async (id: string) => {
    if (!confirm("仅删除此位置配置，不会删除 NAS 文件或已有本地外壳。")) return;
    await updateSettings(
      { nasMappings: settings.nasMappings.filter((item) => item.id !== id) },
      false,
    );
    setStatuses((current) => current.filter((item) => item.mappingId !== id));
  };
  const toggleMapping = async (id: string) => {
    await updateSettings(
      {
        nasMappings: settings.nasMappings.map((item) =>
          item.id === id ? { ...item, enabled: !item.enabled } : item,
        ),
      },
      false,
    );
    await refresh();
  };
  return (
    <div className="storage-card settings-nas-card">
      <div className="nas-heading">
        <div>
          <h3>NAS / 外置存储位置</h3>
          <p>只作为归档目标，不会扫描为媒体库来源。</p>
        </div>
        <div>
          <button
            className="ghost-button"
            onClick={() =>
              setEditing({
                id: crypto.randomUUID(),
                name: "",
                path: "",
                enabled: true,
              })
            }
          >
            新增位置
          </button>
          <button
            className="icon-button"
            title="刷新状态"
            aria-label="刷新 NAS 状态"
            onClick={() => void refresh()}
            disabled={busy}
          >
            <RefreshCw size={15} className={busy ? "spin" : ""} />
          </button>
        </div>
      </div>
      {editing && (
        <div className="nas-editor">
          <input
            value={editing.name}
            onChange={(event) =>
              setEditing({ ...editing, name: event.target.value })
            }
            placeholder="位置名称"
          />
          <div className="input-action">
            <input
              value={editing.path}
              onChange={(event) =>
                setEditing({ ...editing, path: event.target.value })
              }
              placeholder="\\server\share 或 Z:\archive"
            />
            <button
              className="icon-button"
              title="选择目录"
              aria-label="选择 NAS 目录"
              onClick={async () => {
                const value = await window.remake.settings.pickDirectory(
                  editing.path,
                );
                if (value) setEditing({ ...editing, path: value });
              }}
            >
              <FolderOpen size={15} />
            </button>
          </div>
          <div className="nas-editor-actions">
            <button className="ghost-button" onClick={() => setEditing(null)}>
              取消
            </button>
            <button
              className="primary-button"
              onClick={() => void saveMapping()}
              disabled={!editing.name.trim() || !editing.path.trim()}
            >
              保存位置
            </button>
          </div>
        </div>
      )}
      <div className="nas-location-list">
        {settings.nasMappings.map((mapping) => {
          const status = statusFor(mapping.id);
          const label = !mapping.enabled
            ? "已停用"
            : status?.state === "writable"
              ? "在线可写"
              : status?.state === "readonly"
                ? "在线只读"
                : "离线";
          return (
            <div className="nas-location" key={mapping.id}>
              <div className="nas-location-main">
                <span className={`nas-dot ${status?.state || "offline"}`} />
                <div>
                  <strong>{mapping.name}</strong>
                  <code title={mapping.path}>{mapping.path}</code>
                </div>
              </div>
              <div className="nas-location-state">
                <span className={`nas-status ${status?.state || "offline"}`}>
                  {label}
                </span>
                <small title={status?.error}>
                  {status
                    ? `${status.durationMs} ms${status.error ? ` · ${status.error}` : ""}`
                    : "尚未检测"}
                </small>
              </div>
              <button
                className={mapping.enabled ? "switch on" : "switch"}
                title={mapping.enabled ? "停用" : "启用"}
                aria-label={`${mapping.enabled ? "停用" : "启用"} ${mapping.name}`}
                onClick={() => void toggleMapping(mapping.id)}
              >
                <i />
              </button>
              <button
                className="icon-button"
                title="编辑位置"
                aria-label={`编辑 ${mapping.name}`}
                onClick={() => setEditing({ ...mapping })}
              >
                <Settings2 size={14} />
              </button>
              <button
                className="icon-button repkg-delete-button"
                title="删除配置"
                aria-label={`删除 ${mapping.name}`}
                onClick={() => void removeMapping(mapping.id)}
              >
                <Trash2 size={14} />
              </button>
            </div>
          );
        })}
        {!settings.nasMappings.length && (
          <div className="nas-empty">尚未配置 NAS 或外置存储位置</div>
        )}
      </div>
      {message && <div className="notice">{message}</div>}
    </div>
  );
}

interface StorageLogEntry {
  id: string;
  message: string;
  kind: StorageLogKind;
  at: number;
}

function StorageLog({
  entries,
  events,
}: {
  entries: StorageLogEntry[];
  events: TaskEvent[];
}) {
  const rows = [
    ...entries.map((entry) => ({
      id: entry.id,
      message: entry.message,
      kind: entry.kind,
      at: entry.at,
      progress: null as number | null,
    })),
    ...events.map((event) => ({
      id: `task-${event.taskId}`,
      message: event.message || event.status,
      kind: event.status === "failed" ? ("error" as const) : ("info" as const),
      at: Date.now(),
      progress: event.progress,
    })),
  ].slice(0, 20);
  return (
    <aside className="storage-log" aria-label="存储整理操作日志">
      <div className="storage-log-heading">
        <div>
          <h3>操作日志</h3>
          <span>记录当前页面的预检、执行和生成结果</span>
        </div>
        <Terminal size={16} />
      </div>
      <div className="storage-log-list">
        {rows.length ? (
          rows.map((row) => (
            <div className={`storage-log-row ${row.kind}`} key={row.id}>
              <span className="storage-log-dot" />
              <div>
                <p>{row.message}</p>
                <time>
                  {new Date(row.at).toLocaleTimeString("zh-CN", {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })}
                  {row.progress !== null ? ` · ${row.progress}%` : ""}
                </time>
              </div>
            </div>
          ))
        ) : (
          <div className="storage-log-empty">暂无操作记录</div>
        )}
      </div>
    </aside>
  );
}

function NasStorage({
  settings,
  selected,
  onArchived,
  onLog,
}: {
  settings: AppSettings;
  selected: ProjectRecord | null;
  onArchived: (project: ProjectRecord) => Promise<void>;
  onLog: (message: string, kind?: StorageLogKind) => void;
}) {
  const [statuses, setStatuses] = useState<NasLocationStatus[]>([]);
  const [mappingId, setMappingId] = useState("");
  const [plan, setPlan] = useState<NasArchivePlan | null>(null);
  const [action, setAction] = useState<ConflictAction>("rename");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const statusFor = (id: string) =>
    statuses.find((item) => item.mappingId === id);
  const refresh = async () => {
    setBusy(true);
    try {
      const next = await window.remake.storage.checkNasLocations();
      setStatuses(next);
      if (
        !next.some(
          (item) => item.mappingId === mappingId && item.state === "writable",
        )
      )
        setMappingId(
          next.find((item) => item.state === "writable")?.mappingId || "",
        );
    } finally {
      setBusy(false);
    }
  };
  // The archive page checks target health once on entry and after a completed archive.
  useEffect(() => {
    void refresh();
  }, []);
  useEffect(() => {
    setPlan(null);
    setMessage("");
  }, [selected?.id, mappingId]);
  const preview = async () => {
    if (!selected || !mappingId) return;
    setBusy(true);
    setMessage("");
    try {
      const next = await window.remake.storage.previewNasArchive(
        selected.id,
        mappingId,
      );
      setPlan(next);
      setAction("rename");
      const failed = Object.entries(next.checks)
        .filter(([, value]) => !value)
        .map(([key]) => key);
      setMessage(
        failed.length
          ? `预检未通过：${failed.join("、")}`
          : `预检通过 · ${formatFileSize(next.estimatedBytes)}`,
      );
      onLog(
        failed.length
          ? `NAS 预检未通过：${failed.join("、")}`
          : `NAS 预检通过 · ${formatFileSize(next.estimatedBytes)}`,
        failed.length ? "error" : "success",
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setMessage(message);
      onLog(`NAS 预检失败：${message}`, "error");
    } finally {
      setBusy(false);
    }
  };
  const execute = async () => {
    if (!plan) return;
    setBusy(true);
    setMessage("");
    try {
      const result = await window.remake.storage.executeNasArchive(
        plan,
        action,
      );
      setMessage(result.message);
      onLog(result.message, result.success ? "success" : "error");
      if (result.success && result.project) {
        setPlan(null);
        await onArchived(result.project);
        await refresh();
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setMessage(message);
      onLog(`NAS 归档失败：${message}`, "error");
    } finally {
      setBusy(false);
    }
  };
  const rebuildShortcuts = async () => {
    if (!selected?.storagePath) return;
    setBusy(true);
    setMessage("");
    try {
      const result = await window.remake.storage.rebuildNasShortcuts(
        selected.id,
      );
      setMessage(result.message);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : String(error));
    } finally {
      setBusy(false);
    }
  };
  const eligible =
    selected &&
    ["workshop", "backup", "temp"].includes(selected.source) &&
    !selected.storagePath;
  const targetStatus = statusFor(mappingId);
  const checksPassed = plan && Object.values(plan.checks).every(Boolean);
  return (
    <div className="storage-card nas-card">
      <div className="nas-archive nas-archive-only">
        <div>
          <h3>归档到 NAS</h3>
          <div className="migration-source">
            <span>当前项目</span>
            <code title={selected?.rootPath}>
              {selected
                ? `${selected.title} · ${sourceLabels[selected.source]}`
                : "请先从壁纸库选择项目"}
            </code>
          </div>
        </div>
        <label>
          归档位置
          <select
            value={mappingId}
            onChange={(event) => setMappingId(event.target.value)}
          >
            <option value="">选择在线可写位置</option>
            {settings.nasMappings.map((mapping) => (
              <option
                key={mapping.id}
                value={mapping.id}
                disabled={
                  !mapping.enabled ||
                  statusFor(mapping.id)?.state !== "writable"
                }
              >
                {mapping.name} ·{" "}
                {statusFor(mapping.id)?.state === "writable"
                  ? "在线可写"
                  : "不可用"}
              </option>
            ))}
          </select>
        </label>
        {selected && !eligible && !selected.storagePath && (
          <div className="nas-warning">
            仅支持尚未归档的创意工坊、备份或临时项目。
          </div>
        )}
        {plan && (
          <div className="migration-plan">
            <span>NAS 最终路径</span>
            <code title={plan.nasTargetPath}>{plan.nasTargetPath}</code>
            <span>本地外壳</span>
            <code title={plan.localShellPath}>{plan.localShellPath}</code>
            {plan.conflicts.length > 0 && (
              <div
                className="segmented conflict-actions"
                aria-label="NAS 同名项目处理方式"
              >
                <button
                  className={action === "rename" ? "active" : ""}
                  onClick={() => setAction("rename")}
                >
                  自动重命名
                </button>
                <button
                  className={action === "overwrite" ? "active" : ""}
                  onClick={() => setAction("overwrite")}
                >
                  覆盖并备份
                </button>
                <button
                  className={action === "skip" ? "active" : ""}
                  onClick={() => setAction("skip")}
                >
                  跳过
                </button>
              </div>
            )}
          </div>
        )}
        <button
          className="primary-button"
          disabled={
            busy ||
            !eligible ||
            !mappingId ||
            targetStatus?.state !== "writable" ||
            Boolean(plan && !checksPassed)
          }
          onClick={() => void (plan ? execute() : preview())}
        >
          {busy ? "处理中" : plan ? "确认归档" : "预检归档"}
        </button>
        {selected?.storagePath && (
          <button
            className="ghost-button nas-repair-button"
            disabled={busy}
            onClick={() => void rebuildShortcuts()}
          >
            <RefreshCw size={15} className={busy ? "spin" : ""} />
            重建视频快捷方式
          </button>
        )}
        {message && <div className="notice">{message}</div>}
      </div>
    </div>
  );
}

function StoragePanel({
  settings,
  selected,
  onArchived,
  events,
}: {
  settings: AppSettings;
  selected: ProjectRecord | null;
  onArchived: (project: ProjectRecord) => Promise<void>;
  events: TaskEvent[];
}) {
  const [target, setTarget] = useState("");
  const [kind, setKind] = useState<"copy" | "move">("copy");
  const [plan, setPlan] = useState<OperationPlan | null>(null);
  const [conflictAction, setConflictAction] =
    useState<ConflictAction>("rename");
  const [message, setMessage] = useState("");
  const [linkSource, setLinkSource] = useState("");
  const [linkTarget, setLinkTarget] = useState("");
  const [batchSource, setBatchSource] = useState("");
  const [batchTarget, setBatchTarget] = useState("");
  const [importPath, setImportPath] = useState("");
  const [importTitle, setImportTitle] = useState("");
  const [previewPath, setPreviewPath] = useState("");
  const [importMode, setImportMode] = useState<"copy" | "move" | "link">(
    "move",
  );
  const [importDragging, setImportDragging] = useState(false);
  const [importError, setImportError] = useState("");
  const [importSuccess, setImportSuccess] = useState("");
  const [logEntries, setLogEntries] = useState<StorageLogEntry[]>([]);
  const importDragDepth = useRef(0);
  const appendLog = (message: string, kind: StorageLogKind = "info") => {
    setLogEntries((current) => [
      { id: crypto.randomUUID(), message, kind, at: Date.now() },
      ...current,
    ].slice(0, 20));
    void window.remake.storage.appendLog(message, kind).catch(() => undefined);
  };
  // A preview belongs to one project and one operation mode; discard it when either selection changes.
  useEffect(() => {
    setPlan(null);
    setMessage("");
  }, [selected?.id, kind]);
  const preview = async () => {
    if (!selected || !target) return;
    const next = await window.remake.operations.preview({
      kind,
      source: selected.rootPath,
      target,
    });
    setPlan(next);
    setConflictAction("rename");
    setMessage(
      `${next.conflicts.length ? "发现目标冲突" : "预检通过"} · ${formatFileSize(next.estimatedBytes)} · ${next.checks.enoughSpace ? "空间充足" : "空间不足"}`,
    );
    appendLog(
      `${next.conflicts.length ? "迁移预检发现冲突" : "迁移预检通过"} · ${formatFileSize(next.estimatedBytes)}`,
      next.conflicts.length ? "info" : "success",
    );
  };
  const execute = async () => {
    if (!plan) return;
    const result = await window.remake.operations.execute(plan, {
      [plan.target]: plan.conflicts.length ? conflictAction : "skip",
    });
    setMessage(result.message);
    appendLog(result.message, result.success ? "success" : "error");
    if (result.success) setPlan(null);
  };
  const chooseMigrationTarget = async () => {
    const value = await window.remake.settings.pickDirectory(
      target || undefined,
    );
    if (value) {
      setTarget(value);
      setPlan(null);
      setMessage("");
    }
  };
  const acceptImportPath = (value: string) => {
    setImportPath(value);
    if (value) setImportTitle(titleFromPath(value));
    setImportError("");
    setImportSuccess("");
  };
  const chooseImportFile = async () => {
    const value = await window.remake.settings.pickFile();
    if (value) acceptImportPath(value);
  };
  const choosePreviewFile = async () => {
    const value = await window.remake.settings.pickFile([
      {
        name: "图片文件",
        extensions: [
          "jpg",
          "jpeg",
          "png",
          "gif",
          "bmp",
          "webp",
          "avif",
          "tif",
          "tiff",
          "ico",
          "svg",
          "heic",
          "heif",
          "jxl",
        ],
      },
    ]);
    if (value) {
      setPreviewPath(value);
      setImportError("");
      setImportSuccess("");
    }
  };
  const dropImportFile = (event: React.DragEvent<HTMLElement>) => {
    event.preventDefault();
    importDragDepth.current = 0;
    setImportDragging(false);
    const file = event.dataTransfer.files[0];
    if (!file) {
      setImportError("没有识别到可导入的文件");
      return;
    }
    acceptImportPath(window.remake.library.getPathForFile(file));
  };
  const importFile = async () => {
    if (!importPath || !settings.backupPath) return;
    setImportError("");
    setImportSuccess("");
    try {
      const project = await window.remake.library.importFile({
        inputPath: importPath,
        managedDirectory: settings.backupPath,
        mode: importMode,
        title: importTitle,
        previewPath: previewPath || undefined,
      });
      setImportSuccess(
        importMode === "link"
          ? `已生成快捷方式项目：${project.title}`
          : `已生成项目：${project.title}`,
      );
      appendLog(
        importMode === "link"
          ? `已生成快捷方式项目：${project.title}`
          : `已生成项目：${project.title}`,
        "success",
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setImportError(message);
      appendLog(`单文件生成失败：${message}`, "error");
    }
  };
  return (
    <section className="tool-panel">
      <div className="panel-intro">
        <HardDrive size={20} />
        <div>
          <h2>存储整理</h2>
          <p>所有迁移都会先预检、暂存并校验，成功后才提交。</p>
        </div>
      </div>
      <div className="storage-workspace">
        <div className="storage-layout">
        <NasStorage
          settings={settings}
          selected={selected}
          onArchived={onArchived}
          onLog={appendLog}
        />
        <div className="storage-card">
          <h3>批量快捷方式</h3>
          <input
            value={batchSource}
            onChange={(e) => setBatchSource(e.target.value)}
            placeholder="项目源目录"
          />
          <input
            value={batchTarget}
            onChange={(e) => setBatchTarget(e.target.value)}
            placeholder="快捷方式输出目录"
          />
          <button
            className="primary-button"
            onClick={async () => {
              try {
                const rows = await window.remake.storage.createShortcutBatch(
                  batchSource,
                  batchTarget,
                );
                const message = `已处理 ${rows.length} 个快捷方式`;
                setMessage(message);
                appendLog(message, "success");
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                setMessage(message);
                appendLog(`批量生成失败：${message}`, "error");
              }
            }}
            disabled={!batchSource || !batchTarget}
          >
            批量生成
          </button>
        </div>
        <div
          className={
            importDragging
              ? "storage-card import-card dragging"
              : "storage-card import-card"
          }
          onDragEnter={(event) => {
            event.preventDefault();
            importDragDepth.current += 1;
            setImportDragging(true);
          }}
          onDragOver={(event) => {
            event.preventDefault();
            event.dataTransfer.dropEffect = "copy";
          }}
          onDragLeave={() => {
            importDragDepth.current = Math.max(0, importDragDepth.current - 1);
            if (importDragDepth.current === 0) setImportDragging(false);
          }}
          onDrop={dropImportFile}
        >
          <h3>单文件生成项目</h3>
          <div className="import-drop-copy">
            <Upload size={17} />
            <span>
              {importDragging ? "释放文件以识别" : "拖入视频、游戏或程序文件"}
            </span>
          </div>
          <div className="input-action import-file-input">
            <input
              value={importPath}
              onChange={(event) => acceptImportPath(event.target.value)}
              placeholder="选择或拖入文件"
            />
            <button
              className="icon-button"
              type="button"
              title="选择文件"
              aria-label="选择文件"
              onClick={() => void chooseImportFile()}
            >
              <FolderOpen size={15} />
            </button>
          </div>
          {importPath && (
            <div className="import-title">
              <label htmlFor="single-file-title">项目标题</label>
              <input
                id="single-file-title"
                value={importTitle}
                onChange={(event) => setImportTitle(event.target.value)}
                placeholder="输入项目标题"
                maxLength={120}
              />
            </div>
          )}
          <div className="input-action import-file-input">
            <input
              value={previewPath}
              onChange={(event) => {
                setPreviewPath(event.target.value);
                setImportError("");
                setImportSuccess("");
              }}
              placeholder="本地预览图片（可选，自动转 JPG；GIF 保留 GIF）"
            />
            <button
              className="icon-button"
              type="button"
              title="选择本地预览图片"
              aria-label="选择本地预览图片"
              onClick={() => void choosePreviewFile()}
            >
              <Image size={15} />
            </button>
          </div>
          <select
            value={importMode}
            onChange={(event) =>
              setImportMode(event.target.value as typeof importMode)
            }
          >
            <option value="link">保留原位并创建快捷方式</option>
            <option value="copy">复制到项目</option>
            <option value="move">移动到项目</option>
          </select>
          <button
            className="primary-button"
            onClick={() => void importFile()}
            disabled={!importPath || !importTitle.trim() || !settings.backupPath}
          >
            生成项目
          </button>
          {importSuccess && (
            <div className="notice">
              <Check size={15} />
              {importSuccess}
            </div>
          )}
          {importError && (
            <div className="repkg-error" role="alert">
              {importError}
            </div>
          )}
        </div>
        <div className="storage-card">
          <h3>项目迁移</h3>
          <div className="segmented">
            <button
              className={kind === "copy" ? "active" : ""}
              onClick={() => setKind("copy")}
            >
              复制
            </button>
            <button
              className={kind === "move" ? "active" : ""}
              onClick={() => setKind("move")}
            >
              移动
            </button>
          </div>
          <div className="migration-source">
            <span>当前文件夹</span>
            <code title={selected?.rootPath}>
              {selected?.rootPath || "请先从壁纸库选择项目"}
            </code>
          </div>
          <div className="input-action migration-target">
            <input
              value={target}
              onChange={(e) => {
                setTarget(e.target.value);
                setPlan(null);
                setMessage("");
              }}
              placeholder="选择目标父目录"
              disabled={!selected}
            />
            <button
              className="icon-button"
              type="button"
              title="选择目标父目录"
              aria-label="选择目标父目录"
              onClick={() => void chooseMigrationTarget()}
              disabled={!selected}
            >
              <FolderOpen size={15} />
            </button>
          </div>
          {plan && (
            <div className="migration-plan">
              <span>最终路径</span>
              <code title={plan.target}>{plan.target}</code>
              {plan.conflicts.length > 0 && (
                <div
                  className="segmented conflict-actions"
                  aria-label="同名文件夹处理方式"
                >
                  <button
                    className={conflictAction === "rename" ? "active" : ""}
                    onClick={() => setConflictAction("rename")}
                  >
                    自动重命名
                  </button>
                  <button
                    className={conflictAction === "overwrite" ? "active" : ""}
                    onClick={() => setConflictAction("overwrite")}
                  >
                    覆盖
                  </button>
                  <button
                    className={conflictAction === "skip" ? "active" : ""}
                    onClick={() => setConflictAction("skip")}
                  >
                    跳过
                  </button>
                </div>
              )}
            </div>
          )}
          <button
            className="primary-button"
            onClick={() => void (plan ? execute() : preview())}
            disabled={!selected || !target}
          >
            {plan ? "确认执行" : "预检迁移"}
          </button>
          {message && (
            <div className="notice">
              <Check size={15} />
              {message}
            </div>
          )}
        </div>
        <div className="storage-card">
          <h3>目录链接</h3>
          <input
            value={linkSource}
            onChange={(e) => setLinkSource(e.target.value)}
            placeholder="需要保留备份的原目录"
          />
          <input
            value={linkTarget}
            onChange={(e) => setLinkTarget(e.target.value)}
            placeholder="链接指向的目标目录"
          />
          <button
            className="primary-button"
            onClick={async () => {
              try {
                const result = await window.remake.storage.createSymlink(
                  linkSource,
                  linkTarget,
                );
                setMessage(result.message);
                appendLog(result.message, result.success ? "success" : "error");
              } catch (error) {
                const message = error instanceof Error ? error.message : String(error);
                setMessage(message);
                appendLog(`目录链接失败：${message}`, "error");
              }
            }}
            disabled={!linkSource || !linkTarget}
          >
            仅创建链接并保留备份
          </button>
        </div>
        </div>
        <StorageLog entries={logEntries} events={events} />
      </div>
    </section>
  );
}
function SettingsPanel({
  settings,
  updateSettings,
}: {
  settings: AppSettings;
  updateSettings: (
    patch: Partial<AppSettings>,
    rescan?: boolean,
  ) => Promise<void>;
}) {
  const [steam, setSteam] = useState(settings.steamPath);
  const [wallpaper, setWallpaper] = useState(settings.wallpaperPath);
  const [backup, setBackup] = useState(settings.backupPath);
  const [columnCount, setColumnCount] = useState(settings.display.columnCount);
  const [pageSize, setPageSize] = useState(settings.display.pageSize);
  const save = () =>
    void updateSettings({
      steamPath: steam,
      wallpaperPath: wallpaper,
      backupPath: backup,
      display: {
        ...settings.display,
        columnCount,
        pageSize,
      },
    });
  const detect = async () => {
    const found = await window.remake.settings.detectPaths();
    setSteam(found.steamPath || "");
    setWallpaper(found.wallpaperPath || "");
    setBackup(found.backupPath || "");
  };
  const choose = async (current: string, setter: (value: string) => void) => {
    const value = await window.remake.settings.pickDirectory(current);
    if (value) setter(value);
  };
  const addTemp = async () => {
    const value = await window.remake.settings.pickDirectory();
    if (!value) return;
    await updateSettings({
      tempDirectories: [
        ...settings.tempDirectories,
        {
          id: crypto.randomUUID(),
          name: value.split(/[\\/]/).pop() || "临时目录",
          kind: "temp",
          path: value,
          enabled: true,
        },
      ],
    });
  };
  return (
    <section className="tool-panel settings-panel">
      <div className="panel-intro">
        <Settings2 size={20} />
        <div>
          <h2>工作区设置</h2>
          <p>重制版使用独立配置，不会读取或覆盖旧版 config.json。</p>
        </div>
      </div>
      <div className="settings-scroll-area">
        <div className="settings-form">
        <button
          className="ghost-button detect-button"
          onClick={() => void detect()}
        >
          <RefreshCw size={15} />
          从注册表自动识别
        </button>
        <label>
          Steam 路径
          <div className="input-action">
            <input
              value={steam}
              onChange={(e) => setSteam(e.target.value)}
              placeholder="C:\\Program Files (x86)\\Steam"
            />
            <button
              className="icon-button"
              onClick={() => void choose(steam, setSteam)}
            >
              <FolderOpen size={15} />
            </button>
          </div>
        </label>
        <label>
          Wallpaper Engine 路径
          <div className="input-action">
            <input
              value={wallpaper}
              onChange={(e) => setWallpaper(e.target.value)}
              placeholder="Steam\\steamapps\\common\\wallpaper_engine"
            />
            <button
              className="icon-button"
              onClick={() => void choose(wallpaper, setWallpaper)}
            >
              <FolderOpen size={15} />
            </button>
          </div>
        </label>
        <label>
          备份路径
          <div className="input-action">
            <input
              value={backup}
              onChange={(e) => setBackup(e.target.value)}
              placeholder="projects\\backup"
            />
            <button
              className="icon-button"
              onClick={() => void choose(backup, setBackup)}
            >
              <FolderOpen size={15} />
            </button>
          </div>
        </label>
        <div className="settings-display-grid">
          <label>
            最大列数
            <input
              type="number"
              min={2}
              max={10}
              step={1}
              value={columnCount}
              onChange={(event) =>
                setColumnCount(
                  Math.min(10, Math.max(2, Number(event.target.value) || 2)),
                )
              }
            />
          </label>
          <label>
            每页显示数量
            <select
              value={pageSize}
              onChange={(event) => setPageSize(Number(event.target.value))}
            >
              <option value={50}>50</option>
              <option value={100}>100</option>
              <option value={200}>200</option>
            </select>
          </label>
        </div>
        <button className="primary-button" onClick={save}>
          <Check size={15} />
          保存设置
        </button>
        </div>
        <div className="storage-layout">
          <div className="storage-card settings-directory-card">
          <h3>临时目录</h3>
          <button className="ghost-button full" onClick={() => void addTemp()}>
            新增目录
          </button>
          {settings.tempDirectories.map((source) => (
            <div className="source-line" key={source.id}>
              <span title={source.path}>{source.name}</span>
              <div className="source-actions">
                <button
                  className={source.enabled ? "switch on" : "switch"}
                  title={source.enabled ? "停用目录" : "启用目录"}
                  aria-label={source.enabled ? "停用目录" : "启用目录"}
                  onClick={() =>
                    void updateSettings({
                      tempDirectories: settings.tempDirectories.map((item) =>
                        item.id === source.id
                          ? { ...item, enabled: !item.enabled }
                          : item,
                      ),
                    })
                  }
                >
                  <i />
                </button>
                <button
                  className="icon-button repkg-delete-button"
                  type="button"
                  title="删除临时目录配置"
                  aria-label={`删除临时目录 ${source.name}`}
                  onClick={() => {
                    // Only remove the configured source; files in the selected directory must remain untouched.
                    if (
                      !confirm(
                        `确认删除临时目录“${source.name}”的配置？\n不会删除目录中的文件。`,
                      )
                    )
                      return;
                    void updateSettings({
                      tempDirectories: settings.tempDirectories.filter(
                        (item) => item.id !== source.id,
                      ),
                    });
                  }}
                >
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
          </div>
          <NasLocationSettings
            settings={settings}
            updateSettings={updateSettings}
          />
        </div>
      </div>
      <div className="settings-footer">
        <button
          className="ghost-button"
          onClick={async () => {
            if (confirm("这会清空重制版设置，但不会影响旧版配置。")) {
              const next = await window.remake.settings.reset();
              setSteam(next.steamPath);
              setWallpaper(next.wallpaperPath);
              setBackup(next.backupPath);
              setColumnCount(next.display.columnCount);
              setPageSize(next.display.pageSize);
              // Reset writes in the main process; mirror it into App so display settings apply without a restart.
              await updateSettings(next, false);
            }
          }}
        >
          重置设置
        </button>
        <span>配置版本 v{settings.version}</span>
      </div>
    </section>
  );
}
function TaskLog({ events }: { events: TaskEvent[] }) {
  return events.length ? (
    <div className="task-log">
      <h3>最近任务</h3>
      {events.map((event) => (
        <div className="task-row" key={event.taskId}>
          <span>{event.message || event.status}</span>
          <b>{event.progress}%</b>
        </div>
      ))}
    </div>
  ) : null;
}

createRoot(document.getElementById("root")!).render(<App />);
