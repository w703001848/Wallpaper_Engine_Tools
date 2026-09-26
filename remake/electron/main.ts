/** Electron entrypoint: wires typed IPC handlers to filesystem, database and task services. */
import {
  app,
  BrowserWindow,
  clipboard,
  dialog,
  ipcMain,
  shell,
} from "electron";
import path from "node:path";
import fs from "node:fs/promises";
import crypto from "node:crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";
import { SettingsStore } from "./settings.js";
import { LibraryDatabase } from "./database.js";
import { scanFolderTree, scanSources } from "./scanner.js";
import { calculatePathSize } from "./project-capacity.js";
import {
  cancelOperation,
  executeOperation,
  previewOperation,
  createShortcut,
  createSymlink,
  restoreSymlink,
} from "./operations.js";
import { RepkgService } from "./repkg.js";
import {
  createWallpaperProject,
  importSingleFile,
} from "./importer.js";
import { findProjectAsset, projectTypeForAsset } from "./project-asset.js";
import { recalculateProjectSize } from "./project-size.js";
import {
  appendStorageLog,
  clearStorageLog,
  type StorageLogKind,
} from "./storage-log.js";
import {
  readProjectManifest,
  writeProjectManifests,
} from "./project-sync.js";
import { detectedApplicationPaths, installDirectory } from "./path-utils.js";
import {
  checkNasLocations,
  executeNasArchive,
  mappedDriveRemote,
  mappedDriveUncPath,
  nasShortcutTarget,
  previewNasArchive,
  rebuildNasVideoShortcuts,
} from "./nas-storage.js";
import type {
  AppSettings,
  FilterState,
  ProjectRecord,
  ProjectSource,
  SourceConfig,
} from "../src/shared/types.js";

let window: BrowserWindow;
let settings: SettingsStore;
let database: LibraryDatabase;
let repkg: RepkgService;
let scanGeneration = 0;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const execFileAsync = promisify(execFile);
const imageMimeTypes: Record<string, string> = {
  png: "image/png",
  jpg: "image/jpeg",
  jpeg: "image/jpeg",
  jfif: "image/jpeg",
  gif: "image/gif",
  webp: "image/webp",
  bmp: "image/bmp",
  avif: "image/avif",
};
const resolveShortcut = async (shortcutPath: string) =>
  shell.readShortcutLink(shortcutPath).target;

async function resolveMappedDrivePath(inputPath: string): Promise<string> {
  const normalized = path.win32.normalize(inputPath);
  const drive = path.win32.parse(normalized).root.slice(0, 2);
  if (!/^[A-Za-z]:$/u.test(drive)) return normalized;
  try {
    const { stdout } = await execFileAsync("net.exe", ["use", drive], {
      windowsHide: true,
    });
    const remoteRoot = mappedDriveRemote(stdout);
    return remoteRoot ? mappedDriveUncPath(normalized, remoteRoot) : normalized;
  } catch {
    // Local drives and disconnected mappings remain unchanged.
    return normalized;
  }
}

const emit = (
  event: Parameters<NonNullable<BrowserWindow["webContents"]["send"]>>[1],
) => {
  const message = typeof event.message === "string" ? event.message : event.status;
  void appendStorageLog(
    message,
    event.status === "failed" ? "error" : "info",
  ).catch(() => undefined);
  window?.webContents.send("task.event", event);
};
function buildSources(data: AppSettings): SourceConfig[] {
  const configured = data.sources.filter((item) => item.enabled);
  const paths: SourceConfig[] = [];
  const steamRoot = installDirectory(data.steamPath);
  const wallpaperRoot = installDirectory(data.wallpaperPath);
  if (steamRoot)
    paths.push({
      ...SettingsStore.source(
        "workshop-default",
        "创意工坊",
        "workshop",
        path.join(steamRoot, "steamapps/workshop/content/431960"),
      ),
      metadataFile: wallpaperRoot
        ? path.join(wallpaperRoot, "bin/workshopcache.json")
        : undefined,
    });
  if (data.backupPath)
    paths.push(
      SettingsStore.source(
        "backup-default",
        "本地备份",
        "backup",
        data.backupPath,
      ),
    );
  return [
    ...paths,
    ...data.tempDirectories.filter((item) => item.enabled),
    ...configured,
  ];
}
function filtered(items: ProjectRecord[], filter: FilterState) {
  const query = filter.search.trim().toLowerCase();
  const folderRefs = filter.folderId
    ? database.getFolderRefs(filter.folderId)
    : [];
  const rows = items.filter(
    (item) =>
      (!query ||
        `${item.title} ${item.workshopId} ${item.description}`
          .toLowerCase()
          .includes(query)) &&
      (!filter.sources.length || filter.sources.includes(item.source)) &&
      (!filter.types.length || filter.types.includes(item.type)) &&
      (!filter.folderId ||
        folderRefs.some(
          (ref) =>
            ref === item.workshopId ||
            path.normalize(ref).includes(path.normalize(item.rootPath)),
        )),
  );
  rows.sort((a, b) => {
    if (filter.showInvalid && a.invalid !== b.invalid)
      return a.invalid ? -1 : 1;
    const av = a[filter.sort];
    const bv = b[filter.sort];
    const result = av < bv ? -1 : av > bv ? 1 : 0;
    return filter.descending ? -result : result;
  });
  return rows;
}
async function registryValue(key: string, name: string): Promise<string> {
  try {
    const { stdout } = await execFileAsync(
      "reg.exe",
      ["query", key, "/v", name],
      { windowsHide: true },
    );
    return (
      stdout
        .split(/\r?\n/)
        .map((line) => line.trim())
        .find((line) => line.startsWith(name))
        ?.split(/REG_\w+\s+/)[1]
        ?.trim() || ""
    );
  } catch {
    return "";
  }
}
function registerIpc() {
  ipcMain.handle("settings.get", () => settings.get());
  ipcMain.handle("settings.update", async (_e, patch) => {
    const next = await settings.update(patch);
    scanGeneration += 1;
    database.replaceSources(buildSources(next));
    return next;
  });
  ipcMain.handle("settings.reset", async () => {
    const reset = await settings.reset();
    database.reset();
    setTimeout(() => {
      app.relaunch();
      app.exit(0);
    }, 200);
    return reset;
  });
  ipcMain.handle("settings.detectPaths", async () => {
    const steamValue = await registryValue(
      "HKCU\\Software\\Valve\\Steam",
      "SteamPath",
    );
    const wallpaperValue = await registryValue(
      "HKCU\\Software\\WallpaperEngine",
      "installPath",
    );
    return detectedApplicationPaths(steamValue, wallpaperValue);
  });
  ipcMain.handle("settings.pickDirectory", async (_e, defaultPath) => {
    const result = await dialog.showOpenDialog(window, {
      defaultPath: defaultPath || undefined,
      properties: ["openDirectory", "createDirectory"],
    });
    return result.canceled ? null : result.filePaths[0];
  });
  ipcMain.handle("settings.pickFile", async (_e, filters) => {
    const result = await dialog.showOpenDialog(window, {
      properties: ["openFile"],
      filters,
    });
    return result.canceled ? null : result.filePaths[0];
  });
  ipcMain.handle("library.scan", async () => {
    const taskId = crypto.randomUUID();
    const generation = ++scanGeneration;
    void (async () => {
      const snapshot = settings.get();
      const sources = buildSources(snapshot);
      database.replaceSources(sources);
      const rows = await scanSources(
        sources,
        (count) =>
          emit({
            taskId,
            kind: "scan",
            status: "running",
            progress: Math.min(95, count),
            message: `已扫描 ${count} 个目录`,
          }),
        resolveShortcut,
      );
      const wallpaperRoot = installDirectory(snapshot.wallpaperPath);
      const folders = wallpaperRoot
        ? await scanFolderTree(path.join(wallpaperRoot, "config.json"))
        : [];
      // A newer settings change or scan owns the cache; stale asynchronous results must never restore old paths.
      if (generation !== scanGeneration) {
        emit({
          taskId,
          kind: "scan",
          status: "cancelled",
          progress: 100,
          message: "来源设置已变化，本次扫描结果已忽略",
        });
        return;
      }
      database.replaceProjects(rows);
      database.replaceFolders(folders);
      emit({
        taskId,
        kind: "scan",
        status: "completed",
        progress: 100,
        message: `索引 ${rows.length} 个项目`,
      });
    })().catch((error) =>
      emit({
        taskId,
        kind: "scan",
        status: "failed",
        progress: 100,
        message: String(error),
      }),
    );
    return { taskId };
  });
  ipcMain.handle("library.list", (_e, query: { filter: FilterState }) => {
    const rows = filtered(database.list(), query.filter);
    const start = (query.filter.page - 1) * query.filter.pageSize;
    return {
      items: rows.slice(start, start + query.filter.pageSize),
      total: rows.length,
      page: query.filter.page,
      pageCount: Math.max(1, Math.ceil(rows.length / query.filter.pageSize)),
    };
  });
  ipcMain.handle("library.get", (_e, id) => database.get(id));
  ipcMain.handle("library.folders", () => database.listFolders());
  ipcMain.handle("library.getThumbnail", async (_e, target: string) => {
    try {
      const ext = path.extname(target).toLowerCase().slice(1);
      const mime = imageMimeTypes[ext] || "image/jpeg";
      return `data:${mime};base64,${(await fs.readFile(target)).toString("base64")}`;
    } catch {
      return null;
    }
  });
  ipcMain.handle("library.updateMetadata", async (_e, id, patch) => {
    const project = database.get(id);
    if (!project) throw new Error("项目不存在");
    let data: Record<string, unknown> = {};
    let missingManifest = false;
    try {
      data = await readProjectManifest(project.projectPath);
    } catch {
      missingManifest = true;
    }
    let repairedProject = project;
    if (missingManifest) {
      const asset = await findProjectAsset(
        project.rootPath,
        undefined,
        resolveShortcut,
      );
      if (!asset) throw new Error("目录中未找到支持的项目文件或快捷方式");
      const fileSize = await calculatePathSize(asset.targetPath);
      const type = projectTypeForAsset(asset.targetPath);
      const timestamp = Math.floor(Date.now() / 1000);
      data = createWallpaperProject(
        patch.title || path.parse(asset.targetPath).name,
        type,
        asset.manifestFile,
        fileSize,
        timestamp,
        project.previewPath ? path.basename(project.previewPath) : undefined,
      );
      repairedProject = {
        ...project,
        type,
        fileSize,
        invalid: false,
        missingProject: false,
        updatedAt: timestamp * 1000,
      };
    }
    const metadataPatch = {
      title: patch.title,
      description: patch.description,
      favorite: patch.favorite,
      tags: patch.tags,
      updatedate: Date.now(),
    };
    await writeProjectManifests(project, data, metadataPatch);
    if (missingManifest) {
      const repaired = {
        ...repairedProject,
        title: patch.title,
        description: patch.description,
        favorite: patch.favorite,
        tags: patch.tags,
      };
      database.upsertProjects([repaired]);
      return repaired;
    }
    return database.updateMetadata(id, patch);
  });
  ipcMain.handle("library.recalculateSize", async (_e, id) => {
    const project = database.get(id);
    if (!project) throw new Error("项目不存在");
    const fileSize = await recalculateProjectSize(project, resolveShortcut);
    return database.updateSize(id, fileSize);
  });
  ipcMain.handle("library.importFile", async (_e, request) => {
    const shortcutInput =
      request.mode === "link"
        ? await resolveMappedDrivePath(request.inputPath)
        : request.inputPath;
    const project = await importSingleFile({
      ...request,
      // Resolve this in the trusted main process so renderer input cannot select an unrelated shortcut target.
      shortcutTargetPath:
        request.mode === "link"
          ? nasShortcutTarget(shortcutInput, settings.get().nasMappings)
          : undefined,
    });
    database.upsertProjects([project]);
    return project;
  });
  ipcMain.handle(
    "library.relocateAfterMove",
    async (
      _e,
      id: string,
      newRootPath: string,
      destination: "backup" | "temp",
    ) => {
      const project = database.get(id);
      if (!project) throw new Error("项目不存在");
      const configuredRoots =
        destination === "backup"
          ? [settings.get().backupPath]
          : settings
              .get()
              .tempDirectories.filter((item) => item.enabled)
              .map((item) => item.path);
      const normalizedRoot = path.resolve(newRootPath);
      const normalizedParent = path.dirname(normalizedRoot).toLocaleLowerCase();
      // Only accept a direct child of the configured destination; the renderer cannot rebind arbitrary index paths.
      if (
        !configuredRoots.some(
          (root) =>
            root && path.resolve(root).toLocaleLowerCase() === normalizedParent,
        )
      )
        throw new Error("移动结果不属于已配置的目标目录");
      if (!(await fs.stat(normalizedRoot)).isDirectory())
        throw new Error("移动后的项目目录不存在");
      const movedPreview = project.previewPath
        ? path.join(
            normalizedRoot,
            path.relative(project.rootPath, project.previewPath),
          )
        : null;
      const shortcutName =
        `${path.basename(normalizedRoot)}.lnk`.toLocaleLowerCase();
      const hasNasShortcut = (await fs.readdir(normalizedRoot)).some(
        (name) => name.toLocaleLowerCase() === shortcutName,
      );
      const nextSource: ProjectSource =
        destination === "backup" && (project.storagePath || hasNasShortcut)
          ? "nas"
          : destination;
      const moved: ProjectRecord = {
        ...project,
        source: nextSource,
        rootPath: normalizedRoot,
        projectPath: path.join(normalizedRoot, "project.json"),
        previewPath: movedPreview,
        updatedAt: Date.now(),
      };
      // Persist the moved row without a scan so filters, sorting and pagination remain untouched in the renderer.
      scanGeneration += 1;
      database.upsertProjects([moved]);
      return moved;
    },
  );
  ipcMain.handle("library.copyText", (_e, text: string) => {
    // Keep clipboard access in the main process so packaged builds do not depend on browser permissions.
    clipboard.writeText(String(text));
  });
  ipcMain.handle("library.openPath", (_e, target) => shell.openPath(target));
  ipcMain.handle("operations.preview", (_e, input) => previewOperation(input));
  ipcMain.handle("operations.execute", (_e, plan, actions) =>
    executeOperation(plan, actions, database),
  );
  ipcMain.handle("operations.cancel", (_e, id) => cancelOperation(id));
  ipcMain.handle("operations.getLog", (_e, id) => database.getOperation(id));
  ipcMain.handle("storage.createSymlink", (_e, source, target) =>
    createSymlink(source, target),
  );
  ipcMain.handle("storage.restoreSymlink", (_e, link, backup) =>
    restoreSymlink(link, backup),
  );
  ipcMain.handle("storage.createShortcut", (_e, shortcut, target) =>
    createShortcut(shortcut, target),
  );
  ipcMain.handle("storage.createShortcutBatch", async (_e, source, target) => {
    const entries = await fs.readdir(source, { withFileTypes: true });
    await fs.mkdir(target, { recursive: true });
    return Promise.all(
      entries
        .filter((entry) => entry.isDirectory())
        .map((entry) =>
          createShortcut(
            path.join(target, `${entry.name}.lnk`),
            path.join(source, entry.name),
          ),
        ),
    );
  });
  ipcMain.handle("storage.checkNasLocations", () =>
    checkNasLocations(settings.get().nasMappings),
  );
  ipcMain.handle(
    "storage.previewNasArchive",
    async (_e, projectId: string, mappingId: string) => {
      const project = database.get(projectId);
      const mapping = settings
        .get()
        .nasMappings.find((item) => item.id === mappingId);
      if (!project) throw new Error("项目不存在");
      if (!mapping) throw new Error("NAS 位置不存在");
      return previewNasArchive(project, mapping, settings.get().backupPath);
    },
  );
  ipcMain.handle("storage.executeNasArchive", async (_e, plan, action) => {
    const project = database.get(plan.projectId);
    const mapping = settings
      .get()
      .nasMappings.find((item) => item.id === plan.mappingId);
    if (!project) throw new Error("项目不存在");
    if (!mapping) throw new Error("NAS 位置不存在");
    // Archive owns the latest filesystem state; invalidate older scans before they can replace its shell row.
    scanGeneration += 1;
    return executeNasArchive(
      plan,
      action,
      project,
      mapping,
      settings.get().backupPath,
      database,
    );
  });
  ipcMain.handle(
    "storage.rebuildNasShortcuts",
    async (_e, projectId: string) => {
      const project = database.get(projectId);
      if (!project) throw new Error("项目不存在");
      const result = await rebuildNasVideoShortcuts(project);
      database.saveOperation(result);
      return result;
    },
  );
  ipcMain.handle(
    "storage.appendLog",
    (_e, message: string, kind: StorageLogKind = "info") =>
      appendStorageLog(message, kind),
  );
  ipcMain.handle("repkg.start", (_e, input) => repkg.start(input));
  ipcMain.handle("repkg.cancel", (_e, id) => repkg.cancel(id));
  ipcMain.handle("repkg.getOutput", (_e, id) => repkg.getOutput(id));
  ipcMain.handle("repkg.listHistory", () => repkg.listHistory());
  ipcMain.handle("repkg.deleteOutput", (_e, id) => repkg.deleteOutput(id));
  ipcMain.handle("diagnostics.getEnvironment", () => ({
    platform: process.platform,
    arch: process.arch,
    version: app.getVersion(),
    userData: app.getPath("userData"),
    packaged: String(app.isPackaged),
  }));
}
async function createWindow() {
  window = new BrowserWindow({
    width: 1500,
    height: 940,
    minWidth: 1100,
    minHeight: 700,
    backgroundColor: "#11151b",
    webPreferences: {
      preload: path.join(__dirname, "preload.cjs"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  if (process.argv.includes("--dev"))
    await window.loadURL("http://localhost:5173");
  else await window.loadFile(path.join(__dirname, "../../dist/index.html"));
}
app.whenReady().then(async () => {
  // Each launch starts a fresh session log instead of accumulating records from older runs.
  await clearStorageLog();
  settings = new SettingsStore();
  await settings.load();
  database = new LibraryDatabase();
  repkg = new RepkgService((event) => emit(event));
  await repkg.cleanupExpiredOutputs();
  registerIpc();
  await createWindow();
  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) void createWindow();
  });
});
app.on("window-all-closed", () => {
  database?.close();
  if (process.platform !== "darwin") app.quit();
});
