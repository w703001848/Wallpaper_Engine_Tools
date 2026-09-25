/** Creates a managed Wallpaper Engine project from one local file without touching legacy data. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import type { ImportFileRequest, ProjectRecord, ProjectType } from '../src/shared/types.js';
import { createShortcut } from './operations.js';

const safeName = (value: string) => value.replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').trim() || '未命名项目';
async function nextDirectory(root: string, name: string): Promise<string> { let candidate = path.join(root, name); let n = 1; while (true) { try { await fs.access(candidate); candidate = path.join(root, `${name} (${n++})`); } catch { return candidate; } } }
const projectType = (input: string): ProjectType => ['.exe', '.bat', '.cmd'].includes(path.extname(input).toLowerCase()) ? 'application' : 'video';

export async function importSingleFile(request: ImportFileRequest): Promise<ProjectRecord> {
  const input = path.resolve(request.inputPath); const managed = path.resolve(request.managedDirectory); const inputStat = await fs.stat(input); if (!inputStat.isFile()) throw new Error('导入源必须是文件');
  await fs.mkdir(managed, { recursive: true }); const root = await nextDirectory(managed, safeName(request.title)); await fs.mkdir(root); const base = path.basename(input); let file = base;
  try {
    if (request.mode === 'copy') await fs.copyFile(input, path.join(root, base));
    else if (request.mode === 'move') { try { await fs.rename(input, path.join(root, base)); } catch (error: unknown) { if ((error as NodeJS.ErrnoException).code !== 'EXDEV') throw error; await fs.copyFile(input, path.join(root, base)); if ((await fs.stat(path.join(root, base))).size !== inputStat.size) throw new Error('跨磁盘移动校验失败'); await fs.unlink(input); } }
    else { file = `${path.parse(base).name}.lnk`; const shortcut = await createShortcut(path.join(root, file), input); if (!shortcut.success) throw new Error(shortcut.message); }
    let preview = ''; if (request.previewPath) { preview = `preview${path.extname(request.previewPath) || '.jpg'}`; await fs.copyFile(request.previewPath, path.join(root, preview)); }
    const now = Date.now(); const data = { title: request.title, type: projectType(input), file, preview, description: '', subscriptiondate: now, updatedate: now, filesize: inputStat.size };
    const projectPath = path.join(root, 'project.json'); await fs.writeFile(`${projectPath}.tmp`, JSON.stringify(data, null, 2), 'utf8'); await fs.rename(`${projectPath}.tmp`, projectPath);
    return { id: crypto.createHash('sha1').update(`backup:${root}`).digest('hex'), workshopId: path.basename(root), title: request.title, type: data.type, source: 'backup', rootPath: root, projectPath, previewPath: preview ? path.join(root, preview) : null, description: '', authorSteamId: '', fileSize: inputStat.size, updatedAt: now, subscriptionDate: now, invalid: false, missingProject: false, favorite: false, tags: [] };
  } catch (error) { await fs.rm(root, { recursive: true, force: true }); throw error; }
}
