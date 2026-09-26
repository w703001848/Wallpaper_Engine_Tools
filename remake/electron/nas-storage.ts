/** NAS location checks and transactional archive workflow for local wallpaper projects. */
import fs from "node:fs/promises";
import { constants } from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import type {
  ConflictAction,
  NasArchivePlan,
  NasArchiveResult,
  NasLocationStatus,
  NasMapping,
  OperationResult,
  ProjectRecord,
} from "../src/shared/types.js";
import type { LibraryDatabase } from "./database.js";
import { completeWallpaperProject } from "./importer.js";
import { createShortcut } from "./operations.js";
import { isVideoAssetPath } from "./project-asset.js";

const exists = async (target: string): Promise<boolean> => {
  try {
    await fs.lstat(target);
    return true;
  } catch {
    return false;
  }
};
export async function pathBytes(target: string): Promise<number> {
  const stat = await fs.lstat(target);
  if (stat.isFile()) return stat.size;
  let total = 0;
  for (const entry of await fs.readdir(target))
    total += await pathBytes(path.join(target, entry));
  return total;
}
async function hasSpace(root: string, required: number): Promise<boolean> {
  try {
    const info = await fs.statfs(root);
    return Number(info.bavail) * Number(info.bsize) >= required;
  } catch {
    return false;
  }
}
async function uniquePath(target: string): Promise<string> {
  if (!(await exists(target))) return target;
  let index = 1;
  while (await exists(`${target} (${index})`)) index += 1;
  return `${target} (${index})`;
}
const errorText = (error: unknown) =>
  error instanceof Error ? error.message : String(error);

const canFallbackFromRename = (error: unknown) =>
  ["EPERM", "EACCES", "EXDEV"].includes(
    String((error as NodeJS.ErrnoException)?.code || ""),
  );

export async function commitNasStage(
  stage: string,
  target: string,
  rename: typeof fs.rename = fs.rename,
): Promise<"renamed" | "copied"> {
  try {
    await rename(stage, target);
    return "renamed";
  } catch (error) {
    if (!canFallbackFromRename(error) || (await exists(target))) throw error;
  }
  // Some SMB servers allow create/write/delete but reject directory rename; copy-commit preserves compatibility.
  try {
    await fs.cp(stage, target, {
      recursive: true,
      force: false,
      errorOnExist: true,
    });
    if ((await pathBytes(target)) !== (await pathBytes(stage)))
      throw new Error("NAS 最终目录校验失败，文件字节数不一致");
    await fs.rm(stage, { recursive: true, force: true });
    return "copied";
  } catch (error) {
    // A partial fallback target must not be mistaken for a completed archive on retry.
    await fs
      .rm(target, { recursive: true, force: true })
      .catch(() => undefined);
    throw error;
  }
}

type AccessCheck = (target: string, mode: number) => Promise<void>;

async function withTimeout<T>(work: Promise<T>, timeoutMs: number): Promise<T> {
  let timer: NodeJS.Timeout | undefined;
  try {
    return await Promise.race([
      work,
      new Promise<never>((_, reject) => {
        timer = setTimeout(
          () => reject(new Error(`检测超时（${timeoutMs} ms）`)),
          timeoutMs,
        );
      }),
    ]);
  } finally {
    if (timer) clearTimeout(timer);
  }
}

export async function checkNasLocation(
  mapping: NasMapping,
  timeoutMs = 3000,
  access: AccessCheck = fs.access,
): Promise<NasLocationStatus> {
  const started = Date.now();
  if (!mapping.enabled)
    return {
      mappingId: mapping.id,
      state: "offline",
      durationMs: 0,
      error: "位置已停用",
    };
  try {
    // Network shares may wait on Windows reconnects, so both permission checks have a fixed response deadline.
    await withTimeout(access(mapping.path, constants.R_OK), timeoutMs);
    try {
      await withTimeout(access(mapping.path, constants.W_OK), timeoutMs);
      return {
        mappingId: mapping.id,
        state: "writable",
        durationMs: Date.now() - started,
      };
    } catch (error) {
      return {
        mappingId: mapping.id,
        state: "readonly",
        durationMs: Date.now() - started,
        error: errorText(error),
      };
    }
  } catch (error) {
    return {
      mappingId: mapping.id,
      state: "offline",
      durationMs: Date.now() - started,
      error: errorText(error),
    };
  }
}

export async function checkNasLocations(
  mappings: NasMapping[],
  timeoutMs = 3000,
): Promise<NasLocationStatus[]> {
  return Promise.all(
    mappings.map((mapping) => checkNasLocation(mapping, timeoutMs)),
  );
}

function archiveName(project: ProjectRecord): string {
  return (
    (project.workshopId || path.basename(project.rootPath))
      .replace(/[<>:"/\\|?*\x00-\x1f]/g, "_")
      .trim() || "未命名项目"
  );
}

function uncParts(value: string): { host: string; segments: string[] } | null {
  const normalized = path.win32.normalize(value.trim().replaceAll("/", "\\"));
  const match = /^\\\\([^\\]+)\\(.+)$/u.exec(normalized);
  if (!match) return null;
  return {
    host: match[1],
    segments: match[2].split("\\").filter(Boolean),
  };
}

const isIpv4 = (value: string) => {
  const octets = value.split(".");
  return (
    octets.length === 4 &&
    octets.every((item) => /^\d{1,3}$/u.test(item) && Number(item) <= 255)
  );
};

export function mappedDriveRemote(netUseOutput: string): string | null {
  // `net use <drive>` is localized, but its remote value is always the only UNC path in the output.
  return netUseOutput.match(/\\\\[^\r\n]+/u)?.[0].trim() || null;
}

export function mappedDriveUncPath(
  inputPath: string,
  remoteRoot: string,
): string {
  const normalized = path.win32.normalize(inputPath);
  const driveRoot = path.win32.parse(normalized).root;
  if (!/^[A-Za-z]:\\$/u.test(driveRoot)) return normalized;
  return path.win32.join(
    remoteRoot,
    path.win32.relative(driveRoot, normalized),
  );
}

export function nasShortcutTarget(
  inputPath: string,
  mappings: NasMapping[],
): string {
  const input = path.win32.normalize(inputPath);
  const inputUnc = uncParts(input);
  for (const mapping of mappings) {
    if (!mapping.enabled) continue;
    const root = path.win32.normalize(mapping.path);
    const rootUnc = uncParts(root);
    if (!rootUnc || !isIpv4(rootUnc.host)) continue;

    const relative = path.win32.relative(root, input);
    if (
      relative &&
      relative !== ".." &&
      !relative.startsWith("..\\") &&
      !path.win32.isAbsolute(relative)
    )
      return path.win32.join(root, relative);

    // File pickers can return a NAS hostname alias; match the share/subdirectory tail and replace only its host.
    if (
      inputUnc &&
      inputUnc.segments.length > rootUnc.segments.length &&
      rootUnc.segments.every(
        (segment, index) =>
          segment.toLowerCase() === inputUnc.segments[index]?.toLowerCase(),
      )
    ) {
      return path.win32.join(
        root,
        ...inputUnc.segments.slice(rootUnc.segments.length),
      );
    }
  }
  return input;
}

export async function previewNasArchive(
  project: ProjectRecord,
  mapping: NasMapping,
  backupPath: string,
): Promise<NasArchivePlan> {
  // Workshop items also archive directly; the backup shell keeps Wallpaper Engine metadata locally discoverable.
  const eligibleSource =
    ["workshop", "backup", "temp"].includes(project.source) &&
    !project.storagePath;
  const sourceExists = await exists(project.rootPath);
  const status = await checkNasLocation(mapping);
  const estimatedBytes = sourceExists ? await pathBytes(project.rootPath) : 0;
  const nasTargetPath = path.win32.join(mapping.path, archiveName(project));
  const localShellPath =
    project.source === "backup"
      ? project.rootPath
      : path.resolve(backupPath, archiveName(project));
  const localShellAvailable =
    project.source === "backup" || !(await exists(localShellPath));
  let backupWritable = false;
  try {
    await fs.access(
      project.source === "backup" ? path.dirname(project.rootPath) : backupPath,
      constants.W_OK,
    );
    backupWritable = true;
  } catch {
    /* Reported in checks. */
  }
  const targetExists = await exists(nasTargetPath);
  return {
    id: crypto.randomUUID(),
    projectId: project.id,
    mappingId: mapping.id,
    sourcePath: project.rootPath,
    nasTargetPath,
    localShellPath,
    estimatedBytes,
    conflicts: targetExists
      ? [
          {
            source: project.rootPath,
            target: nasTargetPath,
            defaultAction: "rename",
          },
        ]
      : [],
    checks: {
      eligibleSource,
      sourceExists,
      backupWritable,
      nasWritable: status.state === "writable",
      enoughSpace:
        status.state === "writable" &&
        (await hasSpace(mapping.path, estimatedBytes)),
      localShellAvailable,
    },
    status,
  };
}

type ShortcutCreator = typeof createShortcut;

async function archivedVideoFiles(
  root: string,
  current = root,
): Promise<string[]> {
  const result: string[] = [];
  for (const entry of await fs.readdir(current, { withFileTypes: true })) {
    const fullPath = path.join(current, entry.name);
    if (entry.isDirectory())
      result.push(...(await archivedVideoFiles(root, fullPath)));
    else if (entry.isFile() && isVideoAssetPath(entry.name))
      result.push(path.relative(root, fullPath));
  }
  // Stable ordering makes shortcut creation and rollback diagnostics reproducible.
  return result.sort((left, right) => left.localeCompare(right));
}

export async function rebuildNasVideoShortcuts(
  project: ProjectRecord,
  shortcutCreator: ShortcutCreator = createShortcut,
): Promise<OperationResult> {
  const result: OperationResult = {
    id: crypto.randomUUID(),
    success: false,
    message: "",
    changedPaths: [],
    rollbackAvailable: false,
  };
  try {
    if (!project.storagePath) throw new Error("该项目没有 NAS 存储路径");
    if (!(await exists(project.storagePath)))
      throw new Error("NAS 项目目录不可用");
    const videos = await archivedVideoFiles(project.storagePath);
    if (!videos.length) throw new Error("NAS 项目内未找到支持的视频文件");
    for (const relativeVideo of videos) {
      const shortcutPath = path.join(project.rootPath, `${relativeVideo}.lnk`);
      if (await exists(shortcutPath)) continue;
      await fs.mkdir(path.dirname(shortcutPath), { recursive: true });
      const shortcut = await shortcutCreator(
        shortcutPath,
        path.win32.join(project.storagePath, relativeVideo),
      );
      if (!shortcut.success)
        throw new Error(
          `视频快捷方式创建失败（${relativeVideo}）：${shortcut.message}`,
        );
      result.changedPaths.push(shortcutPath);
    }
    result.success = true;
    result.message = result.changedPaths.length
      ? `已补建 ${result.changedPaths.length} 个视频快捷方式`
      : "所有视频快捷方式均已存在";
  } catch (error) {
    // Repair never overwrites existing links, so removing this run's additions fully restores the shell.
    await Promise.all(
      result.changedPaths.map((target) =>
        fs.rm(target, { force: true }).catch(() => undefined),
      ),
    );
    result.changedPaths = [];
    result.message = errorText(error);
  }
  return result;
}

async function archiveContent(
  project: ProjectRecord,
  manifest: Record<string, unknown>,
): Promise<{ relativePath: string; bytes: number } | null> {
  const declared =
    typeof manifest.file === "string" ? manifest.file.trim() : "";
  if (!declared) return null;
  const candidate = path.isAbsolute(declared)
    ? path.normalize(declared)
    : path.resolve(project.rootPath, declared);
  const relativePath = path.relative(project.rootPath, candidate);
  // Only content copied with the project may be referenced from the NAS archive.
  if (
    !relativePath ||
    relativePath === ".." ||
    relativePath.startsWith(`..${path.sep}`) ||
    path.isAbsolute(relativePath) ||
    !(await exists(candidate))
  )
    return null;
  return { relativePath, bytes: await pathBytes(candidate) };
}

async function buildLocalShell(
  project: ProjectRecord,
  shellStage: string,
  nasTarget: string,
  archivedManifest: Record<string, unknown>,
  contentRelativePath: string | null,
  shortcutCreator: ShortcutCreator,
): Promise<{ manifest: Record<string, unknown>; previewPath: string | null }> {
  await fs.mkdir(shellStage, { recursive: true });
  const manifest = { ...archivedManifest };
  let previewPath: string | null = null;
  if (project.previewPath && (await exists(project.previewPath))) {
    const name = path.basename(project.previewPath);
    previewPath = path.join(shellStage, name);
    await fs.copyFile(project.previewPath, previewPath);
    manifest.preview = name;
  }
  // Use the committed target folder name so conflict-renamed archives get a matching shortcut name.
  const directoryShortcutName = `${path.win32.basename(nasTarget)}.lnk`;
  const directoryLink = await shortcutCreator(
    path.join(shellStage, directoryShortcutName),
    nasTarget,
  );
  if (!directoryLink.success)
    throw new Error(`项目快捷方式创建失败：${directoryLink.message}`);
  if (contentRelativePath) {
    const nasContent = path.win32.join(nasTarget, contentRelativePath);
    // The manifest uses the real NAS asset because Wallpaper Engine does not launch .lnk files as media.
    manifest.file = nasContent;
  }
  if (project.type === "video") {
    const videos = await archivedVideoFiles(nasTarget);
    // A valid manifest normally points at one of these files; retain it as a fallback for unusual extensions.
    if (contentRelativePath && !videos.includes(contentRelativePath))
      videos.unshift(contentRelativePath);
    for (const relativeVideo of videos) {
      const nasVideo = path.win32.join(nasTarget, relativeVideo);
      // Mirroring relative folders prevents videos with the same basename from overwriting each other's shortcut.
      const shortcutPath = path.join(shellStage, `${relativeVideo}.lnk`);
      await fs.mkdir(path.dirname(shortcutPath), { recursive: true });
      const contentLink = await shortcutCreator(shortcutPath, nasVideo);
      if (!contentLink.success)
        throw new Error(
          `视频快捷方式创建失败（${relativeVideo}）：${contentLink.message}`,
        );
    }
  } else if (contentRelativePath) {
    const contentLink = await shortcutCreator(
      path.join(shellStage, "打开项目内容.lnk"),
      path.win32.join(nasTarget, contentRelativePath),
    );
    if (!contentLink.success)
      throw new Error(`内容快捷方式创建失败：${contentLink.message}`);
  }
  await fs.writeFile(
    path.join(shellStage, "project.json"),
    JSON.stringify(manifest, null, 2),
    "utf8",
  );
  return { manifest, previewPath };
}

export async function executeNasArchive(
  plan: NasArchivePlan,
  action: ConflictAction,
  project: ProjectRecord,
  mapping: NasMapping,
  backupPath: string,
  database: LibraryDatabase,
  shortcutCreator: ShortcutCreator = createShortcut,
): Promise<NasArchiveResult> {
  const result: NasArchiveResult = {
    id: plan.id,
    success: false,
    message: "",
    changedPaths: [],
    rollbackAvailable: false,
  };
  let nasTarget = plan.nasTargetPath;
  const nasStage = `${plan.nasTargetPath}.wet-staging-${plan.id}`;
  let shellStage = `${plan.localShellPath}.wet-shell-${plan.id}`;
  const sourceBackup = `${project.rootPath}.wet-source-${plan.id}`;
  let displacedNas = "";
  let sourceMoved = false;
  let nasCommitted = false;
  let shellCommitted = false;
  try {
    if (
      project.id !== plan.projectId ||
      mapping.id !== plan.mappingId ||
      project.rootPath !== plan.sourcePath
    )
      throw new Error("归档计划已过期，请重新预检");
    const fresh = await previewNasArchive(project, mapping, backupPath);
    // Plans cross an IPC trust boundary; paths are recomputed from persisted project and settings before any write.
    if (
      plan.nasTargetPath !== fresh.nasTargetPath ||
      plan.localShellPath !== fresh.localShellPath
    )
      throw new Error("归档路径已变化，请重新预检");
    if (!["rename", "overwrite", "skip"].includes(action))
      throw new Error("无效的冲突处理方式");
    const checks = fresh.checks;
    if (!checks.eligibleSource)
      throw new Error("只允许归档未归档的创意工坊、备份或临时项目");
    if (!checks.sourceExists) throw new Error("源项目已不存在");
    if (!checks.backupWritable) throw new Error("本地外壳目录不可写");
    if (!checks.nasWritable)
      throw new Error(
        `NAS 当前不可写：${fresh.status.error || fresh.status.state}`,
      );
    if (!checks.enoughSpace) throw new Error("NAS 可用空间不足");
    if (!checks.localShellAvailable)
      throw new Error("本地备份目录已有同 ID 项目，请先处理冲突");
    if (await exists(nasTarget)) {
      if (action === "skip") throw new Error("NAS 目标已存在，已按选择跳过");
      if (action === "rename") nasTarget = await uniquePath(nasTarget);
    }
    await fs.cp(project.rootPath, nasStage, {
      recursive: true,
      force: false,
      errorOnExist: true,
    });
    if ((await pathBytes(nasStage)) !== fresh.estimatedBytes)
      throw new Error("NAS 暂存内容校验失败，文件字节数不一致");
    let sourceManifest: Record<string, unknown>;
    try {
      sourceManifest = JSON.parse(
        await fs.readFile(project.projectPath, "utf8"),
      ) as Record<string, unknown>;
    } catch {
      throw new Error("无法读取源项目 project.json");
    }
    const content = await archiveContent(project, sourceManifest);
    const contentBytes = content?.bytes ?? fresh.estimatedBytes;
    const archivedManifest = {
      ...completeWallpaperProject(
        sourceManifest,
        contentBytes,
        Math.floor(Date.now() / 1000),
      ),
      storagepath: nasTarget,
    };
    // Keep the NAS copy self-contained and normalized; the shell gets a NAS-absolute file path below.
    await fs.writeFile(
      path.join(nasStage, "project.json"),
      JSON.stringify(archivedManifest, null, 2),
      "utf8",
    );
    if (action === "overwrite" && (await exists(nasTarget))) {
      displacedNas = `${nasTarget}.wet-backup-${plan.id}`;
      await fs.rename(nasTarget, displacedNas);
    }
    // Commit NAS first so Windows creates shortcuts against targets that already exist.
    await commitNasStage(nasStage, nasTarget);
    nasCommitted = true;
    shellStage = `${plan.localShellPath}.wet-shell-${plan.id}`;
    const shell = await buildLocalShell(
      project,
      shellStage,
      nasTarget,
      archivedManifest,
      content?.relativePath ?? null,
      shortcutCreator,
    );
    await fs.rename(project.rootPath, sourceBackup);
    sourceMoved = true;
    await fs.rename(shellStage, plan.localShellPath);
    shellCommitted = true;
    const now = Date.now();
    const shellProject: ProjectRecord = {
      ...project,
      id: crypto
        .createHash("sha1")
        .update(`backup:${plan.localShellPath}`)
        .digest("hex"),
      source: "nas",
      rootPath: plan.localShellPath,
      projectPath: path.join(plan.localShellPath, "project.json"),
      previewPath: shell.previewPath
        ? path.join(plan.localShellPath, path.basename(shell.previewPath))
        : null,
      storagePath: nasTarget,
      fileSize: contentBytes,
      updatedAt: now,
      invalid: false,
      missingProject: false,
    };
    // Index update happens only after filesystem commit so the UI can never point at a half-built shell.
    database.upsertProjects([shellProject]);
    if (project.id !== shellProject.id) database.removeProject(project.id);
    await fs.rm(sourceBackup, { recursive: true, force: true });
    sourceMoved = false;
    result.success = true;
    result.message = displacedNas
      ? `已归档到 NAS，并将原目标备份到 ${displacedNas}`
      : "已归档到 NAS，并生成本地项目外壳";
    result.changedPaths.push(nasTarget, plan.localShellPath);
    if (displacedNas) result.changedPaths.push(displacedNas);
    result.project = shellProject;
  } catch (error) {
    // Reverse commit order: remove shell, restore source, then restore the displaced NAS target.
    if (shellCommitted)
      await fs
        .rm(plan.localShellPath, { recursive: true, force: true })
        .catch(() => undefined);
    if (sourceMoved && (await exists(sourceBackup)))
      await fs.rename(sourceBackup, project.rootPath).catch(() => undefined);
    if (nasCommitted)
      await fs
        .rm(nasTarget, { recursive: true, force: true })
        .catch(() => undefined);
    if (
      displacedNas &&
      (await exists(displacedNas)) &&
      !(await exists(plan.nasTargetPath))
    )
      await fs.rename(displacedNas, plan.nasTargetPath).catch(() => undefined);
    await fs
      .rm(nasStage, { recursive: true, force: true })
      .catch(() => undefined);
    await fs
      .rm(shellStage, { recursive: true, force: true })
      .catch(() => undefined);
    result.message = errorText(error);
  }
  database.saveOperation(result);
  return result;
}
