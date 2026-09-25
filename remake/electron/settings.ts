/** Versioned JSON settings. It intentionally starts clean and never mutates the legacy config.json. */
import { app } from 'electron';
import fs from 'node:fs/promises';
import path from 'node:path';
import type { AppSettings, SourceConfig } from '../src/shared/types.js';

const defaults = (): AppSettings => ({
  version: 1, steamPath: '', wallpaperPath: '', backupPath: '', sources: [], tempDirectories: [], nasMappings: [],
  display: { pageSize: 30, cardSize: 'comfortable', theme: 'dark' },
});

export class SettingsStore {
  private readonly filePath = path.join(app.getPath('userData'), 'settings.json');
  private data: AppSettings = defaults();

  async load(): Promise<AppSettings> {
    try { this.data = { ...defaults(), ...JSON.parse(await fs.readFile(this.filePath, 'utf8')) }; }
    catch { await this.save(); }
    return this.data;
  }
  get(): AppSettings { return this.data; }
  async update(patch: Partial<AppSettings>): Promise<AppSettings> { this.data = { ...this.data, ...patch }; await this.save(); return this.data; }
  async reset(): Promise<AppSettings> { this.data = defaults(); await this.save(); return this.data; }
  async save(): Promise<void> { await fs.mkdir(path.dirname(this.filePath), { recursive: true }); await fs.writeFile(this.filePath, JSON.stringify(this.data, null, 2), 'utf8'); }
  static source(id: string, name: string, kind: SourceConfig['kind'], pathValue: string): SourceConfig { return { id, name, kind, path: path.resolve(pathValue), enabled: true }; }
}
