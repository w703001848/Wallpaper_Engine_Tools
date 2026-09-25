/** Filesystem scanner that turns Wallpaper Engine folders into stable ProjectRecord values. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import type { FolderNode, ProjectRecord, ProjectSource, ProjectType, SourceConfig } from '../src/shared/types.js';

const typeOf = (value: unknown): ProjectType => { const type = String(value || '').toLowerCase(); return ['scene', 'video', 'web', 'application'].includes(type) ? type as ProjectType : 'unknown'; };
export async function calculatePathSize(dir: string): Promise<number> { let total = 0; for (const entry of await fs.readdir(dir, { withFileTypes: true })) { const full = path.join(dir, entry.name); if (entry.isDirectory()) total += await calculatePathSize(full); else if (entry.isFile()) total += (await fs.stat(full)).size; } return total; }
async function firstPreview(root: string, project: Record<string, unknown>): Promise<string | null> { const candidate = typeof project.preview === 'string' ? path.resolve(root, project.preview) : ''; if (candidate && await exists(candidate)) return candidate; for (const name of ['preview.jpg', 'preview.png', 'preview.gif', 'folder.jpg', 'folder.png']) { const full = path.join(root, name); if (await exists(full)) return full; } return null; }
async function exists(target: string): Promise<boolean> { try { await fs.access(target); return true; } catch { return false; } }

export async function scanSource(source: SourceConfig, onProgress?: (count: number) => void): Promise<ProjectRecord[]> {
  if (!source.enabled || !(await exists(source.path))) return [];
  const result: ProjectRecord[] = []; const entries = await fs.readdir(source.path, { withFileTypes: true }); let count = 0; const cache = new Map<string, Record<string, unknown>>();
  if (source.metadataFile && await exists(source.metadataFile)) { try { const raw = JSON.parse(await fs.readFile(source.metadataFile, 'utf8')); const values = Array.isArray(raw.wallpapers) ? raw.wallpapers : []; values.forEach((item: Record<string, unknown>) => cache.set(String(item.workshopid), item)); } catch { /* A broken cache must not prevent folder scanning. */ } }
  for (const entry of entries) { if (!entry.isDirectory()) continue; const root = path.resolve(source.path, entry.name); const projectPath = path.join(root, 'project.json'); let data: Record<string, unknown> = {}; let missing = false;
    try { data = JSON.parse(await fs.readFile(projectPath, 'utf8')); } catch { missing = true; }
    data = { ...(cache.get(entry.name) || {}), ...data }; if (typeof data.previewsmall === 'string' && data.previewsmall.startsWith('http://wpx.internal/__file/')) { data.preview = decodeURIComponent(data.previewsmall.slice('http://wpx.internal/__file/'.length)); }
    const stat = await fs.stat(root); const previewPath = await firstPreview(root, data); const id = crypto.createHash('sha1').update(`${source.kind}:${root}`).digest('hex');
    result.push({ id, workshopId: String(data.workshopid || entry.name), title: String(data.title || entry.name), type: typeOf(data.type), source: source.kind as ProjectSource, rootPath: root, projectPath, previewPath, description: String(data.description || ''), authorSteamId: String(data.authorsteamid || ''), fileSize: await calculatePathSize(root), updatedAt: stat.mtimeMs, subscriptionDate: Number(data.subscriptiondate || stat.birthtimeMs), invalid: Boolean(data.status === 'invalid'), missingProject: missing, favorite: Boolean(data.favorite), tags: Array.isArray(data.tags) ? data.tags.map(String) : [] });
    onProgress?.(++count);
  }
  return result;
}

export async function scanSources(sources: SourceConfig[], onProgress?: (count: number) => void): Promise<ProjectRecord[]> { const all: ProjectRecord[] = []; for (const source of sources) all.push(...await scanSource(source, onProgress)); return all; }

export async function scanFolderTree(configPath: string): Promise<FolderNode[]> {
  try { const raw = JSON.parse(await fs.readFile(configPath, 'utf8')); const account = Object.values(raw).find((value) => typeof value === 'object' && value !== null && 'general' in value) as { general?: { browser?: { folders?: unknown[] } } } | undefined; const folders = account?.general?.browser?.folders; if (!Array.isArray(folders)) return [];
    const parse = (items: unknown[], parentId: string | null, parentPath: string): FolderNode[] => items.map((item, index) => { const data = item as Record<string, unknown>; const title = String(data.title || `分类 ${index + 1}`); const nodePath = parentPath ? `${parentPath}/${title}` : title; const id = crypto.createHash('sha1').update(nodePath).digest('hex'); const projectRefs = data.items && typeof data.items === 'object' ? Object.keys(data.items) : []; return { id, parentId, title, path: nodePath, projectRefs, children: parse(Array.isArray(data.subfolders) ? data.subfolders : [], id, nodePath) }; }); return parse(folders, null, '');
  } catch { return []; }
}
