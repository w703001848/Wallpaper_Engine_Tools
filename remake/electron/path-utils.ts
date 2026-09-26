/** Normalizes detected application paths before they are used to derive Wallpaper Engine directories. */
import path from 'node:path';

export function installDirectory(value: string): string {
  const normalized = value.trim().replace(/^"(.*)"$/, '$1');
  if (!normalized) return '';

  // Different Wallpaper Engine versions may store either the install directory or an executable in the registry.
  return path.extname(normalized).toLowerCase() === '.exe' ? path.dirname(normalized) : normalized;
}

export function detectedApplicationPaths(steamValue: string, wallpaperValue: string) {
  const steamPath = installDirectory(steamValue);
  const wallpaperPath = installDirectory(wallpaperValue);
  return {
    steamPath,
    wallpaperPath,
    backupPath: wallpaperPath ? path.join(wallpaperPath, 'projects', 'backup') : '',
  };
}
