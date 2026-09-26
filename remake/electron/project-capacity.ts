/** Measures project capacity for local folders, external shortcuts and NAS archives. */
import fs from "node:fs/promises";
import path from "node:path";
import { findProjectAsset, type ShortcutResolver } from "./project-asset.js";

export interface ProjectCapacity {
  fileSize: number;
  externalManifestFile?: string;
}

export async function calculatePathSize(target: string): Promise<number> {
  const stat = await fs.stat(target);
  // Shortcut targets are commonly single media files, while normal projects are directories.
  if (stat.isFile()) return stat.size;
  if (!stat.isDirectory()) return 0;
  let total = 0;
  for (const entry of await fs.readdir(target, { withFileTypes: true })) {
    const full = path.join(target, entry.name);
    if (entry.isDirectory()) total += await calculatePathSize(full);
    else if (entry.isFile()) total += (await fs.stat(full)).size;
  }
  return total;
}

export async function measureProjectCapacity(
  rootPath: string,
  manifest: Record<string, unknown>,
  storagePath: string,
  resolveShortcut: ShortcutResolver,
): Promise<ProjectCapacity> {
  const manifestStoragePath =
    typeof manifest.storagepath === "string"
      ? manifest.storagepath.trim()
      : "";
  const archivedPath = storagePath || manifestStoragePath;
  if (archivedPath) {
    // A NAS shell contains only metadata and links, so measure the complete archived project.
    return { fileSize: await calculatePathSize(archivedPath) };
  }

  const asset = await findProjectAsset(
    rootPath,
    manifest.file,
    resolveShortcut,
  );
  const relativeTarget = asset
    ? path.relative(rootPath, asset.targetPath)
    : "";
  const externalAsset =
    asset &&
    (path.isAbsolute(relativeTarget) ||
      relativeTarget === ".." ||
      relativeTarget.startsWith(`..${path.sep}`));
  // Scene and application projects can depend on sibling files, while external links must measure their target only.
  return {
    fileSize: await calculatePathSize(
      externalAsset ? asset.targetPath : rootPath,
    ),
    externalManifestFile: externalAsset ? asset.manifestFile : undefined,
  };
}
