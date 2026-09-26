/** Isolated RePKG task runner; each extraction receives a unique output directory. */
import { app } from 'electron';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn, type ChildProcess } from 'node:child_process';
import type { RepkgJob, RepkgOutputDirectory, TaskEvent } from '../src/shared/types.js';
import { isRepkgPackage, sortRepkgOutput } from '../src/shared/repkg-files.js';
import { cleanupExpiredDirectories, removeManagedDirectory } from './repkg-cleanup.js';

const outputRetentionMs = 7 * 24 * 60 * 60 * 1000;
const taskDirectoryPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

async function listFilesRecursively(root: string): Promise<string[]> {
  const entries = await fs.readdir(root, { withFileTypes: true });
  const nested = await Promise.all(entries.map((entry) => {
    const fullPath = path.join(root, entry.name);
    return entry.isDirectory() ? listFilesRecursively(fullPath) : entry.isFile() ? [fullPath] : [];
  }));
  return nested.flat();
}

export class RepkgService {
  private readonly jobs = new Map<string, RepkgJob>();
  private readonly processes = new Map<string, ChildProcess>();
  private readonly outputRoot = path.join(app.getPath('userData'), 'repkg');
  constructor(private readonly emit: (event: TaskEvent) => void) {}
  private outputPathForId(id: string): string | null { return taskDirectoryPattern.test(id) ? path.join(this.outputRoot, id) : null; }
  async cleanupExpiredOutputs(now = Date.now()): Promise<number> { const activeOutputs = Array.from(this.jobs.values()).filter((job) => job.status === 'queued' || job.status === 'running').map((job) => job.outputPath); return cleanupExpiredDirectories(this.outputRoot, now - outputRetentionMs, activeOutputs); }
  async start(inputPath: string): Promise<RepkgJob> {
    if (!isRepkgPackage(inputPath)) throw new Error('仅支持 .pkg 或 .mpkg 文件');
    await this.cleanupExpiredOutputs();
    const id = crypto.randomUUID(); const outputPath = path.join(this.outputRoot, id); const job: RepkgJob = { id, inputPath, outputPath, status: 'queued', progress: 0 }; this.jobs.set(id, job);
    await fs.mkdir(outputPath, { recursive: true }); const executable = app.isPackaged ? path.join(process.resourcesPath, 'RePKG.exe') : path.resolve(process.cwd(), '..', 'RePKG.exe');
    job.status = 'running'; this.emit({ taskId: id, kind: 'repkg', status: job.status, progress: 5 });
    const child = spawn(executable, ['extract', '-e', 'tex', '-s', '-o', outputPath, inputPath], { windowsHide: true }); this.processes.set(id, child);
    child.stderr?.on('data', (data) => this.emit({ taskId: id, kind: 'repkg', status: 'running', progress: 50, message: String(data) }));
    child.on('error', (error) => { job.status = 'failed'; job.error = error.message; this.processes.delete(id); this.emit({ taskId: id, kind: 'repkg', status: job.status, progress: 100, message: error.message }); });
    child.on('close', (code) => { if (job.status === 'cancelled') return; job.status = code === 0 ? 'completed' : 'failed'; job.progress = 100; if (code !== 0) job.error = `RePKG 退出码 ${code}`; this.processes.delete(id); this.emit({ taskId: id, kind: 'repkg', status: job.status, progress: 100, message: job.error }); });
    return job;
  }
  async cancel(id: string): Promise<boolean> { const job = this.jobs.get(id); const child = this.processes.get(id); if (!job || !child) return false; job.status = 'cancelled'; child.kill(); this.emit({ taskId: id, kind: 'repkg', status: 'cancelled', progress: job.progress }); return true; }
  async getOutput(id: string): Promise<string[]> { const outputPath = this.jobs.get(id)?.outputPath || this.outputPathForId(id); if (!outputPath) return []; try { return sortRepkgOutput(await listFilesRecursively(outputPath)); } catch { return []; } }
  async deleteOutput(id: string): Promise<boolean> {
    const outputPath = this.outputPathForId(id); if (!outputPath) return false;
    const job = this.jobs.get(id); if (job?.status === 'queued' || job?.status === 'running') throw new Error('正在提取的导出目录不能删除');
    const removed = await removeManagedDirectory(this.outputRoot, id, Array.from(this.processes.keys(), (activeId) => path.join(this.outputRoot, activeId)));
    if (removed) this.jobs.delete(id);
    return removed;
  }
  async listHistory(): Promise<RepkgOutputDirectory[]> {
    const history: RepkgOutputDirectory[] = [];
    try {
      for (const entry of await fs.readdir(this.outputRoot, { withFileTypes: true })) {
        if (!entry.isDirectory() || !taskDirectoryPattern.test(entry.name)) continue;
        const outputPath = path.join(this.outputRoot, entry.name);
        try { history.push({ id: entry.name, outputPath, updatedAt: (await fs.stat(outputPath)).mtimeMs }); } catch { /* A disappearing cleanup target is simply omitted. */ }
      }
    } catch { return []; }
    return history.sort((left, right) => right.updatedAt - left.updatedAt);
  }
}
