/** Filesystem scanner that turns Wallpaper Engine folders into stable ProjectRecord values. */
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import type {
  FolderNode,
  ProjectRecord,
  ProjectSource,
  ProjectType,
  SourceConfig,
} from "../src/shared/types.js";
import { updateWallpaperProjectSize } from "./importer.js";
import {
  measureProjectCapacity,
  type ProjectCapacity,
} from "./project-capacity.js";
import type { ShortcutResolver } from "./project-asset.js";

const typeOf = (value: unknown): ProjectType => {
  const type = String(value || "").toLowerCase();
  return ["scene", "video", "web", "application"].includes(type)
    ? (type as ProjectType)
    : "unknown";
};
const projectType = (
  project: Record<string, unknown>,
  projectsById: Map<string, Record<string, unknown>>,
  visited = new Set<string>(),
): ProjectType => {
  const declaredType = typeOf(project.type);
  if (declaredType !== "unknown") return declaredType;

  const dependency =
    typeof project.dependency === "string" ||
    typeof project.dependency === "number"
      ? String(project.dependency).trim()
      : "";
  if (!dependency || visited.has(dependency)) return "unknown";

  const parent = projectsById.get(dependency);
  if (!parent) return "unknown";

  // Presets may form dependency chains; the visited set prevents malformed cycles from blocking a scan.
  visited.add(dependency);
  return projectType(parent, projectsById, visited);
};
const timestampMs = (value: unknown, fallback: number) => {
  const timestamp = Number(value);
  if (!Number.isFinite(timestamp) || timestamp <= 0) return fallback;
  return timestamp < 1_000_000_000_000 ? timestamp * 1000 : timestamp;
};
const metadataFileSize = (value: unknown): number => {
  const size = Number(value);
  return Number.isFinite(size) && size >= 0 ? size : 0;
};
async function firstPreview(
  root: string,
  project: Record<string, unknown>,
): Promise<string | null> {
  const candidate =
    typeof project.preview === "string"
      ? path.resolve(root, project.preview)
      : "";
  if (candidate && (await exists(candidate))) return candidate;
  for (const name of [
    "preview.jpg",
    "preview.png",
    "preview.gif",
    "folder.jpg",
    "folder.png",
  ]) {
    const full = path.join(root, name);
    if (await exists(full)) return full;
  }
  return null;
}
async function exists(target: string): Promise<boolean> {
  try {
    await fs.access(target);
    return true;
  } catch {
    return false;
  }
}

export async function scanSource(
  source: SourceConfig,
  onProgress?: (count: number) => void,
  resolveShortcut: ShortcutResolver = async () => {
    throw new Error("当前环境无法解析快捷方式");
  },
): Promise<ProjectRecord[]> {
  if (!source.enabled || !(await exists(source.path))) return [];
  const result: ProjectRecord[] = [];
  const entries = await fs.readdir(source.path, { withFileTypes: true });
  let count = 0;
  const cache = new Map<string, Record<string, unknown>>();
  if (source.metadataFile && (await exists(source.metadataFile))) {
    try {
      const raw = JSON.parse(await fs.readFile(source.metadataFile, "utf8"));
      const values = Array.isArray(raw.wallpapers) ? raw.wallpapers : [];
      values.forEach((item: Record<string, unknown>) => {
        const workshopId = String(item.workshopid ?? "").trim();
        if (workshopId) cache.set(workshopId, item);
      });
    } catch {
      /* A broken cache must not prevent folder scanning. */
    }
  }
  const manifests = new Map<
    string,
    { data: Record<string, unknown>; missing: boolean; hasFileSize: boolean }
  >();
  const projectsById = new Map(cache);
  // Build the dependency index before producing rows so inheritance never depends on directory order.
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const projectPath = path.join(source.path, entry.name, "project.json");
    let manifest: Record<string, unknown> = {};
    let missing = false;
    try {
      manifest = JSON.parse(await fs.readFile(projectPath, "utf8"));
    } catch {
      missing = true;
    }
    const hasFileSize =
      typeof manifest.filesize === "number" &&
      Number.isFinite(manifest.filesize) &&
      manifest.filesize >= 0;
    const data = { ...(cache.get(entry.name) || {}), ...manifest };
    manifests.set(entry.name, { data, missing, hasFileSize });
    projectsById.set(String(data.workshopid || entry.name), data);
  }
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const root = path.resolve(source.path, entry.name);
    const projectPath = path.join(root, "project.json");
    const { data, missing, hasFileSize } = manifests.get(entry.name) ?? {
      data: {},
      missing: true,
      hasFileSize: false,
    };
    if (
      typeof data.previewsmall === "string" &&
      data.previewsmall.startsWith("http://wpx.internal/__file/")
    ) {
      data.preview = decodeURIComponent(
        data.previewsmall.slice("http://wpx.internal/__file/".length),
      );
    }
    const stat = await fs.stat(root);
    const previewPath = await firstPreview(root, data);
    const storagePath =
      typeof data.storagepath === "string" ? data.storagepath.trim() : "";
    const directoryShortcutName = `${entry.name}.lnk`.toLocaleLowerCase();
    const hasDirectoryShortcut =
      source.kind === "backup" &&
      (await fs.readdir(root)).some(
        (name) => name.toLocaleLowerCase() === directoryShortcutName,
      );
    // Legacy NAS shells may lack storagepath, but their directory-named shortcut is an explicit archive marker.
    const projectSource: ProjectSource =
      source.kind === "backup" && (storagePath || hasDirectoryShortcut)
        ? "nas"
        : source.kind;
    const id = crypto
      .createHash("sha1")
      .update(`${source.kind}:${root}`)
      .digest("hex");
    // Workshop manifests often omit workshopid, so the directory name is the stable key used by workshopcache.json.
    const missingWorkshopCacheEntry =
      source.kind === "workshop" && !cache.has(entry.name);
    const invalid = missing || missingWorkshopCacheEntry;
    let capacity: ProjectCapacity = {
      fileSize: metadataFileSize(data.filesize),
    };
    if (!hasFileSize) {
      try {
        capacity = await measureProjectCapacity(
          root,
          data,
          storagePath,
          resolveShortcut,
        );
        if (!missing) {
          // Persist the first calculation so later scans stay metadata-only and do not repeatedly traverse the project.
          await updateWallpaperProjectSize(
            projectPath,
            capacity.fileSize,
            Math.floor(timestampMs(data.updatedate, stat.mtimeMs) / 1000),
            capacity.externalManifestFile,
          );
        }
      } catch {
        // An inaccessible NAS path or broken shortcut must not abort the remaining library scan.
      }
    }
    result.push({
      id,
      workshopId: String(data.workshopid || entry.name),
      title: String(data.title || entry.name),
      type: projectType(data, projectsById),
      source: projectSource,
      rootPath: root,
      projectPath,
      previewPath,
      storagePath,
      description: String(data.description || ""),
      authorSteamId: String(data.authorsteamid || ""),
      fileSize: capacity.fileSize,
      updatedAt: timestampMs(data.updatedate, stat.mtimeMs),
      subscriptionDate: timestampMs(data.subscriptiondate, stat.birthtimeMs),
      invalid,
      missingProject: missing,
      favorite: Boolean(data.favorite),
      tags: Array.isArray(data.tags) ? data.tags.map(String) : [],
    });
    onProgress?.(++count);
  }
  return result;
}

export async function scanSources(
  sources: SourceConfig[],
  onProgress?: (count: number) => void,
  resolveShortcut?: ShortcutResolver,
): Promise<ProjectRecord[]> {
  const all: ProjectRecord[] = [];
  for (const source of sources)
    all.push(...(await scanSource(source, onProgress, resolveShortcut)));
  return all;
}

export async function scanFolderTree(
  configPath: string,
): Promise<FolderNode[]> {
  try {
    const raw = JSON.parse(await fs.readFile(configPath, "utf8"));
    const account = Object.values(raw).find(
      (value) =>
        typeof value === "object" && value !== null && "general" in value,
    ) as { general?: { browser?: { folders?: unknown[] } } } | undefined;
    const folders = account?.general?.browser?.folders;
    if (!Array.isArray(folders)) return [];
    const parse = (
      items: unknown[],
      parentId: string | null,
      parentPath: string,
    ): FolderNode[] =>
      items.map((item, index) => {
        const data = item as Record<string, unknown>;
        const title = String(data.title || `分类 ${index + 1}`);
        const nodePath = parentPath ? `${parentPath}/${title}` : title;
        const id = crypto.createHash("sha1").update(nodePath).digest("hex");
        const projectRefs =
          data.items && typeof data.items === "object"
            ? Object.keys(data.items)
            : [];
        return {
          id,
          parentId,
          title,
          path: nodePath,
          projectRefs,
          children: parse(
            Array.isArray(data.subfolders) ? data.subfolders : [],
            id,
            nodePath,
          ),
        };
      });
    return parse(folders, null, "");
  } catch {
    return [];
  }
}
