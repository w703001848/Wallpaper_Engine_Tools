/** Isolated RePKG task runner; each extraction receives a unique output directory. */
import { app } from 'electron';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawn, type ChildProcess } from 'node:child_process';
import type { RepkgJob, TaskEvent } from '../src/shared/types.js';

export class RepkgService {
  private readonly jobs = new Map<string, RepkgJob>();
  private readonly processes = new Map<string, ChildProcess>();
  constructor(private readonly emit: (event: TaskEvent) => void) {}
  async start(inputPath: string): Promise<RepkgJob> {
    const id = crypto.randomUUID(); const outputPath = path.join(app.getPath('userData'), 'repkg', id); const job: RepkgJob = { id, inputPath, outputPath, status: 'queued', progress: 0 }; this.jobs.set(id, job);
    await fs.mkdir(outputPath, { recursive: true }); const executable = app.isPackaged ? path.join(process.resourcesPath, 'RePKG.exe') : path.resolve(process.cwd(), '..', 'RePKG.exe');
    job.status = 'running'; this.emit({ taskId: id, kind: 'repkg', status: job.status, progress: 5 });
    const child = spawn(executable, ['extract', '-e', 'tex', '-s', '-o', outputPath, inputPath], { windowsHide: true }); this.processes.set(id, child);
    child.stderr?.on('data', (data) => this.emit({ taskId: id, kind: 'repkg', status: 'running', progress: 50, message: String(data) }));
    child.on('error', (error) => { job.status = 'failed'; job.error = error.message; this.processes.delete(id); this.emit({ taskId: id, kind: 'repkg', status: job.status, progress: 100, message: error.message }); });
    child.on('close', (code) => { if (job.status === 'cancelled') return; job.status = code === 0 ? 'completed' : 'failed'; job.progress = 100; if (code !== 0) job.error = `RePKG 退出码 ${code}`; this.processes.delete(id); this.emit({ taskId: id, kind: 'repkg', status: job.status, progress: 100, message: job.error }); });
    return job;
  }
  async cancel(id: string): Promise<boolean> { const job = this.jobs.get(id); const child = this.processes.get(id); if (!job || !child) return false; job.status = 'cancelled'; child.kill(); this.emit({ taskId: id, kind: 'repkg', status: 'cancelled', progress: job.progress }); return true; }
  async getOutput(id: string): Promise<string[]> { const job = this.jobs.get(id); if (!job) return []; try { return (await fs.readdir(job.outputPath)).map((name) => path.join(job.outputPath, name)); } catch { return []; } }
}
