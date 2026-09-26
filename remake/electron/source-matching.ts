/** Determines whether cached projects still belong to the currently enabled scan sources. */
import path from 'node:path';
import type { ProjectRecord, SourceConfig } from '../src/shared/types.js';

export function projectBelongsToSources(project: ProjectRecord, sources: SourceConfig[]): boolean {
  return sources.some((source) => {
    // NAS shells are physically owned by the backup scan root even though they have a distinct UI source.
    const sourceMatches = source.kind === project.source
      || (source.kind === 'backup' && project.source === 'nas');
    if (!source.enabled || !sourceMatches) return false;
    const relative = path.relative(path.resolve(source.path), path.resolve(project.rootPath));
    // A source owns its root and descendants, but never sibling paths with the same prefix.
    return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
  });
}
