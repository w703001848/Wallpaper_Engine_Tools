import { describe, expect, it } from 'vitest';
import path from 'node:path';
import fs from 'node:fs/promises';
import os from 'node:os';
import { scanSource } from '../electron/scanner.js';

describe('scanner', () => {
  it('normalizes a project and marks missing project.json', async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), 'wet-remake-')); const valid = path.join(root, '123'); const invalid = path.join(root, 'missing'); await fs.mkdir(valid); await fs.mkdir(invalid); await fs.writeFile(path.join(valid, 'project.json'), JSON.stringify({ title: 'Demo', type: 'scene', preview: 'preview.jpg', tags: ['a'] })); await fs.writeFile(path.join(valid, 'preview.jpg'), 'image');
    const rows = await scanSource({ id: 't', name: 'Test', kind: 'backup', path: root, enabled: true }); expect(rows).toHaveLength(2); expect(rows.find((row) => row.title === 'Demo')?.previewPath).toBe(path.join(valid, 'preview.jpg')); expect(rows.find((row) => row.rootPath === invalid)?.missingProject).toBe(true);
    await fs.rm(root, { recursive: true, force: true });
  });
});
