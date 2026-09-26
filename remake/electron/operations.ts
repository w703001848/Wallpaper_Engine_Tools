/** Safe filesystem operations: preview first, execute with conflict decisions, and persist results. */
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import type { ConflictAction, OperationPlan, OperationResult } from '../src/shared/types.js';
import type { LibraryDatabase } from './database.js';

const cancelled = new Set<string>();
export function cancelOperation(operationId: string): boolean { cancelled.add(operationId); return true; }

const execFileAsync = promisify(execFile);
const id = () => crypto.randomUUID();
async function exists(target: string): Promise<boolean> { try { await fs.lstat(target); return true; } catch { return false; } }
async function bytes(target: string): Promise<number> { const stat = await fs.lstat(target); if (stat.isFile()) return stat.size; let sum = 0; for (const item of await fs.readdir(target)) sum += await bytes(path.join(target, item)); return sum; }
async function writable(dir: string): Promise<boolean> { try { await fs.access(dir, (await import('node:fs')).constants.W_OK); return true; } catch { return false; } }
async function existingParent(target: string): Promise<string> { let current = path.resolve(target); while (!(await exists(current))) { const parent = path.dirname(current); if (parent === current) return current; current = parent; } return current; }
async function hasSpace(parent: string, required: number): Promise<boolean> { try { const info = await fs.statfs(parent); return Number(info.bavail) * Number(info.bsize) >= required; } catch { return false; } }
async function uniquePath(target: string): Promise<string> { if (!(await exists(target))) return target; const ext = path.extname(target); const base = target.slice(0, target.length - ext.length); let n = 1; while (await exists(`${base} (${n})${ext}`)) n++; return `${base} (${n})${ext}`; }

export async function previewOperation(input: Omit<OperationPlan, 'id' | 'estimatedBytes' | 'conflicts' | 'checks'>): Promise<OperationPlan> {
  const source = path.resolve(input.source);
  // Copy and move receive a destination directory. Appending the source name keeps the selected project folder intact.
  const target = input.kind === 'copy' || input.kind === 'move' ? path.join(path.resolve(input.target), path.basename(source)) : path.resolve(input.target);
  const sourceExists = await exists(source); const targetExists = await exists(target); const targetParent = await existingParent(path.dirname(target)); const estimatedBytes = sourceExists ? await bytes(source) : 0;
  return { ...input, source, target, id: id(), estimatedBytes, conflicts: targetExists ? [{ source, target, defaultAction: 'skip' }] : [], checks: { sourceExists, targetParentWritable: await writable(targetParent), enoughSpace: await hasSpace(targetParent, estimatedBytes) } };
}

export async function executeOperation(plan: OperationPlan, actions: Record<string, ConflictAction>, db: LibraryDatabase): Promise<OperationResult> {
  const changed: string[] = []; const result: OperationResult = { id: plan.id, success: false, message: '', changedPaths: changed, rollbackAvailable: false }; let staging = ''; let displaced = '';
  try {
    if (cancelled.delete(plan.id)) throw new Error('操作已取消');
    if (!plan.checks.sourceExists) throw new Error('源路径不存在');
    if (!plan.checks.targetParentWritable) throw new Error('目标目录不可写');
    if (!plan.checks.enoughSpace) throw new Error('目标磁盘可用空间不足');
    let target = plan.target; const action = actions[plan.target] || plan.conflicts[0]?.defaultAction || 'skip';
    if (await exists(target)) { if (action === 'skip') throw new Error('目标已存在，操作已跳过'); if (action === 'rename') target = await uniquePath(target); }
    // Copying into the source tree can recurse, while overwriting the source itself can delete the committed move.
    const relativeTarget = path.relative(path.resolve(plan.source), path.resolve(target));
    if (!relativeTarget || (!relativeTarget.startsWith('..') && !path.isAbsolute(relativeTarget))) throw new Error('目标文件夹不能与源文件夹相同或位于其内部');
    await fs.mkdir(path.dirname(target), { recursive: true });
    // Copy into an isolated staging path first. The destination is only committed after byte validation.
    if (plan.kind === 'copy' || plan.kind === 'move') { staging = `${target}.wet-staging-${plan.id}`; await fs.cp(plan.source, staging, { recursive: true, force: false }); if (cancelled.delete(plan.id)) throw new Error('操作已取消'); if (await bytes(staging) !== plan.estimatedBytes) throw new Error('目标校验失败，文件大小不一致'); if (action === 'overwrite' && await exists(target)) { displaced = `${target}.wet-backup-${plan.id}`; await fs.rename(target, displaced); } await fs.rename(staging, target); staging = ''; if (plan.kind === 'move') await fs.rm(plan.source, { recursive: true, force: true }); }
    else if (plan.kind === 'symlink') { await fs.symlink(plan.source, target, (await fs.lstat(plan.source)).isDirectory() ? 'dir' : 'file'); }
    else throw new Error(`不支持的操作类型: ${plan.kind}`);
    changed.push(target); if (displaced) changed.push(displaced); result.success = true; result.message = '操作完成并通过校验'; result.rollbackAvailable = plan.kind === 'copy' || plan.kind === 'move';
  } catch (error) { if (staging) await fs.rm(staging, { recursive: true, force: true }).catch(() => undefined); if (displaced && !(await exists(plan.target))) await fs.rename(displaced, plan.target).catch(() => undefined); result.message = error instanceof Error ? error.message : String(error); }
  db.saveOperation(result); return result;
}

export async function createShortcut(shortcutPath: string, targetPath: string): Promise<OperationResult> {
  const result: OperationResult = { id: id(), success: false, message: '', changedPaths: [], rollbackAvailable: true };
  try {
    await fs.mkdir(path.dirname(shortcutPath), { recursive: true });
    const script = `$ws=New-Object -ComObject WScript.Shell;$s=$ws.CreateShortcut('${shortcutPath.replaceAll("'", "''")}');$s.TargetPath='${targetPath.replaceAll("'", "''")}';$s.WorkingDirectory='${path.dirname(targetPath).replaceAll("'", "''")}';$s.Save()`;
    await execFileAsync('powershell.exe', ['-NoProfile', '-NonInteractive', '-EncodedCommand', Buffer.from(script, 'utf16le').toString('base64')]);
    result.success = true; result.message = '快捷方式已生成'; result.changedPaths.push(shortcutPath);
  } catch (error) { result.message = error instanceof Error ? error.message : String(error); }
  return result;
}

export async function createSymlink(source: string, target: string): Promise<OperationResult> {
  const result: OperationResult = { id: id(), success: false, message: '', changedPaths: [], rollbackAvailable: true };
  const sourcePath = path.resolve(source); const targetPath = path.resolve(target); const backup = `${sourcePath}.wet-backup`; let sourceRenamed = false; let targetWasCreated = false; let linkCreated = false;
  try {
    if (!(await exists(sourcePath))) throw new Error('需要链接的原目录不存在');
    if (!(await fs.lstat(sourcePath)).isDirectory()) throw new Error('需要链接的源路径必须是目录');
    const sourceToTarget = path.relative(sourcePath, targetPath); const targetToSource = path.relative(targetPath, sourcePath);
    if (!sourceToTarget || !targetToSource || (!sourceToTarget.startsWith('..') && !path.isAbsolute(sourceToTarget)) || (!targetToSource.startsWith('..') && !path.isAbsolute(targetToSource))) throw new Error('原目录与目标目录不能相同或互相包含');
    if (await exists(backup)) throw new Error(`备份目录已存在: ${backup}`);
    if (!(await exists(targetPath))) { await fs.mkdir(targetPath, { recursive: true }); targetWasCreated = true; }
    if (!(await fs.lstat(targetPath)).isDirectory()) throw new Error('目标路径必须是目录');
    await fs.rename(sourcePath, backup); sourceRenamed = true;
    // Windows junctions provide directory redirection without requiring Developer Mode or elevation.
    await fs.symlink(targetPath, sourcePath, process.platform === 'win32' ? 'junction' : 'dir'); linkCreated = true;
    // Pure link mode deliberately leaves the original content only in the recovery backup.
    result.success = true; result.message = `目录链接已创建，未复制原目录内容；备份保留在 ${backup}`; result.changedPaths.push(sourcePath, targetPath, backup);
  } catch (error) {
    if (linkCreated) await fs.unlink(sourcePath).catch(() => undefined);
    if (sourceRenamed && !(await exists(sourcePath))) await fs.rename(backup, sourcePath).catch(() => undefined);
    if (targetWasCreated) await fs.rm(targetPath, { recursive: true, force: true }).catch(() => undefined);
    const cause = error as NodeJS.ErrnoException;
    result.message = cause.code === 'EPERM' ? '没有权限创建目录链接，请确认原目录和目标目录可写，且目标不是受保护或网络位置' : error instanceof Error ? error.message : String(error);
  }
  return result;
}

export async function restoreSymlink(linkPath: string, backupPath: string): Promise<OperationResult> {
  const result: OperationResult = { id: id(), success: false, message: '', changedPaths: [], rollbackAvailable: false };
  try { const stat = await fs.lstat(linkPath); if (!stat.isSymbolicLink()) throw new Error('源路径不是符号链接，已拒绝删除'); if (!(await exists(backupPath))) throw new Error('找不到对应的备份目录'); await fs.unlink(linkPath); await fs.rename(backupPath, linkPath); result.success = true; result.message = '符号链接已恢复'; result.changedPaths.push(linkPath); } catch (error) { result.message = error instanceof Error ? error.message : String(error); } return result;
}
