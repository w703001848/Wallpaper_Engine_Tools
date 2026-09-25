import { describe, expect, it } from 'vitest';
import type { ProjectRecord } from '../src/shared/types.js';

const rows: ProjectRecord[] = [{ id: '1', workshopId: '1', title: 'Alpha', type: 'scene', source: 'workshop', rootPath: '', projectPath: '', previewPath: null, description: '', authorSteamId: '', fileSize: 4, updatedAt: 2, subscriptionDate: 1, invalid: false, missingProject: false, favorite: false, tags: [] }, { id: '2', workshopId: '2', title: 'Beta', type: 'video', source: 'backup', rootPath: '', projectPath: '', previewPath: null, description: '', authorSteamId: '', fileSize: 8, updatedAt: 1, subscriptionDate: 2, invalid: true, missingProject: false, favorite: false, tags: [] }];
describe('filter contract', () => { it('keeps source and invalid semantics explicit', () => { const valid = rows.filter((item) => item.source === 'workshop' && !item.invalid); expect(valid.map((item) => item.title)).toEqual(['Alpha']); }); });
