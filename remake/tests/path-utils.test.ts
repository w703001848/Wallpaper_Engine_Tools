import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { detectedApplicationPaths, installDirectory } from '../electron/path-utils.js';

describe('Wallpaper Engine path detection', () => {
  const installPath = 'C:\\Program Files (x86)\\Steam\\steamapps\\common\\wallpaper_engine';

  it('derives the backup directory when the registry value points to an executable', () => {
    const detected = detectedApplicationPaths('', `${installPath}\\wallpaper64.exe`);

    expect(detected.wallpaperPath).toBe(installPath);
    expect(detected.backupPath).toBe(path.join(installPath, 'projects', 'backup'));
  });

  it('keeps directory registry values unchanged', () => {
    expect(installDirectory(installPath)).toBe(installPath);
  });

  it('accepts quoted executable registry values', () => {
    expect(installDirectory(`"${installPath}\\wallpaper64.exe"`)).toBe(installPath);
  });
});
