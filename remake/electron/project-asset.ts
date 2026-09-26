/** Resolves the real Wallpaper Engine asset behind local files and Windows shortcuts. */
import fs from "node:fs/promises";
import path from "node:path";
import type { ProjectType } from "../src/shared/types.js";

export type ShortcutResolver = (shortcutPath: string) => Promise<string>;

export interface ProjectAsset {
  targetPath: string;
  manifestFile: string;
  shortcutPath: string | null;
}

const applicationExtensions = new Set([".exe", ".bat", ".cmd", ".com", ".scr"]);
const videoExtensions = new Set([
  ".mp4",
  ".webm",
  ".mkv",
  ".avi",
  ".mov",
  ".wmv",
  ".m4v",
  ".mpg",
  ".mpeg",
]);

export function isVideoAssetPath(input: string): boolean {
  return videoExtensions.has(path.extname(input).toLowerCase());
}

export function projectTypeForAsset(input: string): ProjectType {
  if (isVideoAssetPath(input)) return "video";
  // Single-file generation accepts every non-video file as an application asset;
  // this covers archives, documents, scripts and files without an extension.
  return "application";
}

async function isFile(target: string): Promise<boolean> {
  try {
    return (await fs.stat(target)).isFile();
  } catch {
    return false;
  }
}

async function shortcutAsset(
  shortcutPath: string,
  resolveShortcut: ShortcutResolver,
): Promise<ProjectAsset> {
  const targetPath = path.resolve(await resolveShortcut(shortcutPath));
  if (!(await isFile(targetPath)))
    throw new Error(`快捷方式目标不存在: ${targetPath}`);
  // Wallpaper Engine needs the real asset path; the .lnk is only a local pointer.
  return { targetPath, manifestFile: targetPath, shortcutPath };
}

export async function findProjectAsset(
  root: string,
  declaredFile: unknown,
  resolveShortcut: ShortcutResolver,
): Promise<ProjectAsset | null> {
  const declared = typeof declaredFile === "string" ? declaredFile.trim() : "";
  if (declared) {
    const candidate = path.isAbsolute(declared)
      ? path.normalize(declared)
      : path.resolve(root, declared);
    if (path.extname(candidate).toLowerCase() === ".lnk")
      return shortcutAsset(candidate, resolveShortcut);
    if (await isFile(candidate))
      return {
        targetPath: candidate,
        manifestFile: declared,
        shortcutPath: null,
      };

    // Explorer may hide .lnk, so support both "video.mp4.lnk" and "video.lnk" conventions.
    for (const shortcutPath of [
      `${candidate}.lnk`,
      path.join(path.dirname(candidate), `${path.parse(candidate).name}.lnk`),
    ]) {
      if (await isFile(shortcutPath))
        return shortcutAsset(shortcutPath, resolveShortcut);
    }
  }

  const entries = await fs.readdir(root, { withFileTypes: true });
  const files = entries
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name);
  const shortcut = files.find(
    (name) => path.extname(name).toLowerCase() === ".lnk",
  );
  if (shortcut)
    return shortcutAsset(path.join(root, shortcut), resolveShortcut);
  const asset = files.find((name) => {
    if (/^preview\./i.test(name) || name.toLowerCase() === "project.json")
      return false;
    const extension = path.extname(name).toLowerCase();
    return applicationExtensions.has(extension) || isVideoAssetPath(name);
  });
  return asset
    ? {
        targetPath: path.join(root, asset),
        manifestFile: asset,
        shortcutPath: null,
      }
    : null;
}
