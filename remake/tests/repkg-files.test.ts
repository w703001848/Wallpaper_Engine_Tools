/** Verifies RePKG input validation and renderer preview classification. */
import { describe, expect, it } from 'vitest';
import { displayFileName, isPreviewImage, isRepkgPackage, sortRepkgOutput } from '../src/shared/repkg-files.js';

describe('RePKG file types', () => {
  it('accepts package files case-insensitively', () => {
    expect(isRepkgPackage('D:\\wallpapers\\scene.PKG')).toBe(true);
    expect(isRepkgPackage('D:\\wallpapers\\scene.mpkg')).toBe(true);
    expect(isRepkgPackage('D:\\wallpapers\\scene.zip')).toBe(false);
  });

  it('recognizes supported large-image previews', () => {
    expect(isPreviewImage('output\\materials\\preview.PNG')).toBe(true);
    expect(isPreviewImage('output\\readme.txt')).toBe(false);
  });

  it('extracts a display name from Windows and POSIX paths', () => {
    expect(displayFileName('D:\\output\\preview.png')).toBe('preview.png');
    expect(displayFileName('/output/preview.png')).toBe('preview.png');
  });

  it('sorts preview images before other output files', () => {
    expect(sortRepkgOutput(['z.txt', 'b.png', 'a.json', 'a.jpg'])).toEqual(['a.jpg', 'b.png', 'a.json', 'z.txt']);
  });
});
