/** Keeps local shell and archived NAS project manifests synchronized with rollback on partial writes. */
import fs from "node:fs/promises";
import crypto from "node:crypto";
import path from "node:path";
import type { ProjectRecord } from "../src/shared/types.js";

export type ProjectManifest = Record<string, unknown>;

export async function readProjectManifest(
  projectPath: string,
): Promise<ProjectManifest> {
  return JSON.parse(await fs.readFile(projectPath, "utf8")) as ProjectManifest;
}

async function writeJsonAtomically(
  target: string,
  data: ProjectManifest,
): Promise<void> {
  const temporary = `${target}.tmp-${crypto.randomUUID()}`;
  try {
    await fs.writeFile(temporary, JSON.stringify(data, null, 2), "utf8");
    await fs.rename(temporary, target);
  } catch (error) {
    await fs.rm(temporary, { force: true }).catch(() => undefined);
    throw error;
  }
}

function archivedManifestPath(
  project: ProjectRecord,
  manifest: ProjectManifest,
): string {
  const storagePath =
    project.storagePath ||
    (typeof manifest.storagepath === "string" ? manifest.storagepath.trim() : "");
  if (!storagePath) return "";
  return path.join(storagePath, "project.json");
}

export async function writeProjectManifests(
  project: ProjectRecord,
  localManifest: ProjectManifest,
  patch: ProjectManifest,
): Promise<ProjectManifest> {
  const localNext = { ...localManifest, ...patch };
  const remotePath = archivedManifestPath(project, localManifest);
  if (!remotePath) {
    await writeJsonAtomically(project.projectPath, localNext);
    return localNext;
  }

  const remoteOriginal = await readProjectManifest(remotePath);
  const remoteNext = {
    ...remoteOriginal,
    ...patch,
    storagepath:
      typeof remoteOriginal.storagepath === "string"
        ? remoteOriginal.storagepath
        : project.storagePath || localManifest.storagepath,
  };
  // Commit both manifests as one logical operation; restore NAS metadata if the shell write fails.
  await writeJsonAtomically(remotePath, remoteNext);
  try {
    await writeJsonAtomically(project.projectPath, localNext);
  } catch (error) {
    await writeJsonAtomically(remotePath, remoteOriginal).catch(() => undefined);
    throw error;
  }
  return localNext;
}
