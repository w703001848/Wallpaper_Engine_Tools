/** Calculates project capacity and persists it to project.json for local projects and NAS shells. */
import type { ProjectRecord } from "../src/shared/types.js";
import { formatFileSize } from "../src/shared/file-size.js";
import type { ShortcutResolver } from "./project-asset.js";
import { measureProjectCapacity } from "./project-capacity.js";
import {
  readProjectManifest,
  writeProjectManifests,
} from "./project-sync.js";

export async function recalculateProjectSize(
  project: ProjectRecord,
  resolveShortcut: ShortcutResolver,
  timestamp = Math.floor(Date.now() / 1000),
): Promise<number> {
  let manifest: Record<string, unknown> = {};
  try {
    manifest = await readProjectManifest(project.projectPath);
  } catch {
    /* Missing manifests fall back to asset discovery below. */
  }
  const capacity = await measureProjectCapacity(
    project.rootPath,
    manifest,
    project.storagePath,
    resolveShortcut,
  );
  await writeProjectManifests(project, manifest, {
    ...(capacity.externalManifestFile
      ? { file: capacity.externalManifestFile }
      : {}),
    filesize: capacity.fileSize,
    filesizelabel: formatFileSize(capacity.fileSize),
    updatedate: timestamp,
  });
  return capacity.fileSize;
}
