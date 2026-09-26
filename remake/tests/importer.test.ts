/** Verifies single-file imports produce Wallpaper Engine-compatible assets and metadata. */
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, expect, it, vi } from 'vitest';
import { importSingleFile, updateWallpaperProjectSize } from '../electron/importer.js';

vi.mock('electron', () => ({
  nativeImage: {
    createFromPath: () => ({
      isEmpty: () => false,
      toJPEG: () => Buffer.from('converted-jpeg'),
    }),
  },
}));

describe('single-file importer', () => {
  it('uses the video filename as title and generates a preview image', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-video-'));
    try {
      const input = path.join(fixture, 'My Clip.mp4'); const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'video-content', 'utf8');
      const project = await importSingleFile({ inputPath: input, managedDirectory: managed, mode: 'copy' }, async (source, output) => {
        expect(source).toBe(path.join(managed, 'My Clip', 'My Clip.mp4'));
        await fs.writeFile(output, 'jpeg-preview', 'utf8');
      });
      const manifest = JSON.parse(await fs.readFile(project.projectPath, 'utf8')) as Record<string, unknown>;

      expect(project.title).toBe('My Clip');
      expect(manifest).toMatchObject({ title: 'My Clip', type: 'video', file: 'My Clip.mp4', preview: 'preview.jpg', version: 0 });
      expect(manifest).not.toHaveProperty('visibility');
      expect(manifest.general).toEqual({ properties: { schemecolor: { order: 0, text: 'ui_browse_properties_scheme_color', type: 'color', value: '0.2 0.2 0.2' } } });
      expect(manifest).toMatchObject({ ratingsex: '', ratingviolence: '', tags: [], contentrating: '', description: '', allowmobileupload: false, authorsteamid: '', favorite: true, filesize: 13, filesizelabel: '13 B', hasrating: false, ispreset: false, local: false, official: false, rating: 0, ratingrounded: 5, status: '', workshopid: '', workshopurl: '', storagepath: '' });
      expect(manifest.subscriptiondate).toEqual(expect.any(Number));
      expect(manifest.updatedate).toBe(manifest.subscriptiondate);
      await expect(fs.readFile(path.join(project.rootPath, 'preview.jpg'), 'utf8')).resolves.toBe('jpeg-preview');
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('keeps the source and points project.json at a Windows shortcut', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-link-'));
    try {
      const input = path.join(fixture, 'Demo Game.exe'); const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'application-content', 'utf8');
      const project = await importSingleFile({ inputPath: input, managedDirectory: managed, mode: 'link' });
      const manifest = JSON.parse(await fs.readFile(project.projectPath, 'utf8')) as Record<string, unknown>;

      expect(manifest).toMatchObject({ title: 'Demo Game', type: 'application', file: '上传用.exe', version: 0 });
      expect(manifest).not.toHaveProperty('preview');
      await expect(fs.readFile(input, 'utf8')).resolves.toBe('application-content');
      expect((await fs.stat(path.join(project.rootPath, 'Demo Game.lnk'))).isFile()).toBe(true);
      await expect(fs.stat(path.join(project.rootPath, 'Demo Game.exe'))).rejects.toThrow();
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('copies a local JPEG preview into the project as preview.jpg', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-local-preview-'));
    try {
      const input = path.join(fixture, 'Original.exe');
      const localPreview = path.join(fixture, 'cover.JPEG');
      const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'application-content', 'utf8');
      await fs.writeFile(localPreview, 'jpeg-preview', 'utf8');

      const project = await importSingleFile({
        inputPath: input,
        managedDirectory: managed,
        mode: 'move',
        previewPath: localPreview,
      });
      const manifest = JSON.parse(await fs.readFile(project.projectPath, 'utf8')) as Record<string, unknown>;

      expect(manifest.preview).toBe('preview.jpg');
      await expect(fs.readFile(path.join(project.rootPath, 'preview.jpg'), 'utf8')).resolves.toBe('converted-jpeg');
      await expect(fs.readFile(input, 'utf8')).rejects.toThrow();
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('keeps a local GIF preview as preview.gif', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-local-gif-'));
    try {
      const input = path.join(fixture, 'Original.exe');
      const localPreview = path.join(fixture, 'cover.gif');
      const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'application-content', 'utf8');
      await fs.writeFile(localPreview, 'gif-preview', 'utf8');

      const project = await importSingleFile({
        inputPath: input,
        managedDirectory: managed,
        mode: 'copy',
        previewPath: localPreview,
      });

      expect(JSON.parse(await fs.readFile(project.projectPath, 'utf8'))).toMatchObject({ preview: 'preview.gif' });
      await expect(fs.readFile(path.join(project.rootPath, 'preview.gif'), 'utf8')).resolves.toBe('gif-preview');
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('generates an application project for an otherwise unknown file type', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-other-type-'));
    try {
      const input = path.join(fixture, 'Archive.zip'); const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'archive-content', 'utf8');

      const project = await importSingleFile({ inputPath: input, managedDirectory: managed, mode: 'move' });
      const manifest = JSON.parse(await fs.readFile(project.projectPath, 'utf8')) as Record<string, unknown>;

      expect(project.type).toBe('application');
      expect(manifest).toMatchObject({ title: 'Archive', type: 'application', file: '上传用.exe' });
      await expect(fs.readFile(path.join(project.rootPath, 'Archive.zip'), 'utf8')).resolves.toBe('archive-content');
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('uses 上传用.exe in the manifest without renaming the executable', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-upload-name-'));
    try {
      const input = path.join(fixture, 'Original.exe'); const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'application-content', 'utf8');

      const project = await importSingleFile({ inputPath: input, managedDirectory: managed, mode: 'copy' });
      const manifest = JSON.parse(await fs.readFile(project.projectPath, 'utf8')) as Record<string, unknown>;

      expect(manifest).toMatchObject({ type: 'application', file: '上传用.exe' });
      await expect(fs.readFile(path.join(project.rootPath, 'Original.exe'), 'utf8')).resolves.toBe('application-content');
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('uses the normalized NAS address for shortcut projects', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-nas-link-'));
    try {
      const input = path.join(fixture, 'NAS Movie.mp4'); const managed = path.join(fixture, 'projects');
      const shortcutTargetPath = '\\\\192.168.10.101\\hdd0\\videos\\NAS Movie.mp4';
      await fs.writeFile(input, 'video-content', 'utf8');
      const project = await importSingleFile(
        { inputPath: input, managedDirectory: managed, mode: 'link', shortcutTargetPath },
        async (_source, output) => fs.writeFile(output, 'jpeg-preview', 'utf8'),
      );
      const manifest = JSON.parse(await fs.readFile(project.projectPath, 'utf8')) as Record<string, unknown>;

      expect(manifest.file).toBe('NAS Movie.lnk');
      await expect(fs.readFile(input, 'utf8')).resolves.toBe('video-content');
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('restores a moved video when preview extraction fails', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-rollback-'));
    try {
      const input = path.join(fixture, 'Broken Preview.mp4'); const managed = path.join(fixture, 'projects');
      await fs.writeFile(input, 'video-content', 'utf8');

      await expect(importSingleFile({ inputPath: input, managedDirectory: managed, mode: 'move' }, async () => { throw new Error('thumbnail failed'); })).rejects.toThrow('thumbnail failed');

      await expect(fs.readFile(input, 'utf8')).resolves.toBe('video-content');
      await expect(fs.readdir(managed)).resolves.toEqual([]);
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });

  it('writes the recalculated size and display label back to project.json', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-import-size-'));
    try {
      const projectPath = path.join(fixture, 'project.json');
      await fs.writeFile(projectPath, JSON.stringify({ title: 'Demo', filesize: 0, filesizelabel: '' }), 'utf8');

      await updateWallpaperProjectSize(projectPath, 5 * 1024 ** 2, 1700000000);

      const manifest = JSON.parse(await fs.readFile(projectPath, 'utf8')) as Record<string, unknown>;
      expect(manifest).toMatchObject({ title: 'Demo', filesize: 5 * 1024 ** 2, filesizelabel: '5.0 MB', updatedate: 1700000000 });
    } finally { await fs.rm(fixture, { recursive: true, force: true }); }
  });
});
