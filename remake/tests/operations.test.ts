/** Exercises project migration plus directory-link creation and recovery on the real filesystem. */
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { describe, expect, it } from 'vitest';
import type { LibraryDatabase } from '../electron/database.js';
import { createSymlink, executeOperation, previewOperation, restoreSymlink } from '../electron/operations.js';

describe('project migration', () => {
  it('keeps the selected source directory as a child of the destination', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-project-migration-'));
    const source = path.join(fixture, 'source', '123456'); const destination = path.join(fixture, 'destination');
    await fs.mkdir(source, { recursive: true }); await fs.mkdir(destination); await fs.writeFile(path.join(source, 'project.json'), '{}', 'utf8');

    const plan = await previewOperation({ kind: 'copy', source, target: destination });
    const database = { saveOperation: () => undefined } as unknown as LibraryDatabase;
    const result = await executeOperation(plan, {}, database);

    expect(plan.source).toBe(path.resolve(source));
    expect(plan.target).toBe(path.join(destination, '123456'));
    expect(plan.conflicts).toEqual([]);
    expect(result.success, result.message).toBe(true);
    await expect(fs.readFile(path.join(destination, '123456', 'project.json'), 'utf8')).resolves.toBe('{}');
    await expect(fs.stat(path.join(destination, 'project.json'))).rejects.toThrow();
    await fs.rm(fixture, { recursive: true, force: true });
  });

  it('rejects overwriting the selected source directory itself', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-project-same-target-'));
    const source = path.join(fixture, '123456');
    await fs.mkdir(source); await fs.writeFile(path.join(source, 'project.json'), '{}', 'utf8');

    const plan = await previewOperation({ kind: 'move', source, target: fixture });
    const database = { saveOperation: () => undefined } as unknown as LibraryDatabase;
    const result = await executeOperation(plan, { [plan.target]: 'overwrite' }, database);

    expect(result.success).toBe(false);
    expect(result.message).toContain('目标文件夹不能与源文件夹相同');
    await expect(fs.readFile(path.join(source, 'project.json'), 'utf8')).resolves.toBe('{}');
    await fs.rm(fixture, { recursive: true, force: true });
  });
});

describe('directory links', () => {
  it('creates only a directory link without copying source content', async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-directory-link-'));
    const source = path.join(fixture, 'source'); const target = path.join(fixture, 'target'); const backup = `${source}.wet-backup`;
    await Promise.all([fs.mkdir(source), fs.mkdir(target)]); await fs.writeFile(path.join(source, 'project.json'), '{"title":"demo"}', 'utf8'); await fs.writeFile(path.join(target, 'target.txt'), 'existing', 'utf8');

    const created = await createSymlink(source, target);
    expect(created.success, created.message).toBe(true);
    expect((await fs.lstat(source)).isSymbolicLink()).toBe(true);
    await expect(fs.readFile(path.join(source, 'target.txt'), 'utf8')).resolves.toBe('existing');
    await expect(fs.stat(path.join(target, 'project.json'))).rejects.toThrow();
    await expect(fs.readFile(path.join(backup, 'project.json'), 'utf8')).resolves.toContain('demo');

    const restored = await restoreSymlink(source, backup);
    expect(restored.success, restored.message).toBe(true);
    expect((await fs.lstat(source)).isSymbolicLink()).toBe(false);
    await expect(fs.readFile(path.join(source, 'project.json'), 'utf8')).resolves.toContain('demo');
    await fs.rm(fixture, { recursive: true, force: true });
  });
});
