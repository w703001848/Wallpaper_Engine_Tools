/** Removes expired RePKG task directories within the app-managed output root only. */
import fs from 'node:fs/promises';
import path from 'node:path';

const normalizedPath = (value: string): string => path.resolve(value).toLowerCase();

export async function removeManagedDirectory(rootPath: string, directoryName: string, protectedPaths: Iterable<string> = []): Promise<boolean> {
  const root = path.resolve(rootPath); const target = path.resolve(root, directoryName); const relative = path.relative(root, target);
  const protectedSet = new Set(Array.from(protectedPaths, normalizedPath));
  // Manual deletion accepts one direct child name only; paths and traversal segments are never followed.
  if (!directoryName || path.basename(directoryName) !== directoryName || !relative || relative.startsWith('..') || path.isAbsolute(relative) || protectedSet.has(normalizedPath(target))) return false;
  try { const stat = await fs.lstat(target); if (!stat.isDirectory() || stat.isSymbolicLink()) return false; await fs.rm(target, { recursive: true, force: false }); return true; }
  catch { return false; }
}

export async function cleanupExpiredDirectories(rootPath: string, cutoff: number, protectedPaths: Iterable<string> = []): Promise<number> {
  const root = path.resolve(rootPath);
  const protectedSet = new Set(Array.from(protectedPaths, normalizedPath));
  let entries;
  try { entries = await fs.readdir(root, { withFileTypes: true }); } catch { return 0; }
  let removed = 0;
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    const target = path.resolve(root, entry.name);
    const relative = path.relative(root, target);
    // Recursive deletion is allowed only for a direct child of the app-owned RePKG root.
    if (!relative || relative.startsWith('..') || path.isAbsolute(relative) || protectedSet.has(normalizedPath(target))) continue;
    try {
      if ((await fs.stat(target)).mtimeMs >= cutoff) continue;
      await fs.rm(target, { recursive: true, force: true });
      removed += 1;
    } catch { /* Cleanup is best-effort and must not block application startup or extraction. */ }
  }
  return removed;
}
