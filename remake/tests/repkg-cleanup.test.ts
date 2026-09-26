/** Verifies bounded cleanup of expired app-managed RePKG output directories. */
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import { cleanupExpiredDirectories, removeManagedDirectory } from '../electron/repkg-cleanup.js';

describe('RePKG output cleanup', () => {
  it('removes only expired unprotected task directories', async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-repkg-cleanup-'));
    const expired = path.join(root, 'expired'); const current = path.join(root, 'current'); const protectedPath = path.join(root, 'protected');
    await Promise.all([fs.mkdir(expired), fs.mkdir(current), fs.mkdir(protectedPath), fs.writeFile(path.join(root, 'keep.txt'), 'file')]);
    const oldTime = new Date('2020-01-01T00:00:00Z'); const currentTime = new Date('2026-01-01T00:00:00Z');
    await Promise.all([fs.utimes(expired, oldTime, oldTime), fs.utimes(protectedPath, oldTime, oldTime), fs.utimes(current, currentTime, currentTime)]);

    expect(await cleanupExpiredDirectories(root, currentTime.getTime(), [protectedPath])).toBe(1);
    await expect(fs.stat(expired)).rejects.toThrow();
    await expect(fs.stat(current)).resolves.toBeDefined();
    await expect(fs.stat(protectedPath)).resolves.toBeDefined();
    await expect(fs.readFile(path.join(root, 'keep.txt'), 'utf8')).resolves.toBe('file');
    await fs.rm(root, { recursive: true, force: true });
  });

  it('manually removes only an unprotected direct child', async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-repkg-delete-')); const removable = path.join(root, 'removable'); const protectedPath = path.join(root, 'protected'); const outside = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-repkg-outside-'));
    await Promise.all([fs.mkdir(removable), fs.mkdir(protectedPath)]);
    expect(await removeManagedDirectory(root, 'removable')).toBe(true);
    expect(await removeManagedDirectory(root, 'protected', [protectedPath])).toBe(false);
    expect(await removeManagedDirectory(root, `..${path.sep}${path.basename(outside)}`)).toBe(false);
    await expect(fs.stat(protectedPath)).resolves.toBeDefined();
    await expect(fs.stat(outside)).resolves.toBeDefined();
    await Promise.all([fs.rm(root, { recursive: true, force: true }), fs.rm(outside, { recursive: true, force: true })]);
  });
});
