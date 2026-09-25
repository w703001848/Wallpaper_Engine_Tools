/** Shared contracts between the Electron main process and React renderer. */

export type ProjectSource = 'workshop' | 'backup' | 'temp' | 'nas' | 'unknown';
export type ProjectType = 'scene' | 'video' | 'web' | 'application' | 'unknown';

export interface ProjectRecord {
  id: string;
  workshopId: string;
  title: string;
  type: ProjectType;
  source: ProjectSource;
  rootPath: string;
  projectPath: string;
  previewPath: string | null;
  description: string;
  authorSteamId: string;
  fileSize: number;
  updatedAt: number;
  subscriptionDate: number;
  invalid: boolean;
  missingProject: boolean;
  favorite: boolean;
  tags: string[];
}

export interface SourceConfig {
  id: string;
  name: string;
  kind: ProjectSource;
  path: string;
  enabled: boolean;
  metadataFile?: string;
}

export interface FolderNode { id: string; parentId: string | null; title: string; path: string; projectRefs: string[]; children: FolderNode[]; }

export interface AppSettings {
  version: 1;
  steamPath: string;
  wallpaperPath: string;
  backupPath: string;
  sources: SourceConfig[];
  tempDirectories: SourceConfig[];
  nasMappings: { id: string; name: string; path: string; enabled: boolean }[];
  display: { pageSize: number; cardSize: 'compact' | 'comfortable'; theme: 'dark' | 'light' };
}

export interface FilterState {
  search: string;
  sources: ProjectSource[];
  types: ProjectType[];
  showInvalid: boolean;
  sort: 'title' | 'updatedAt' | 'fileSize' | 'subscriptionDate';
  descending: boolean;
  page: number;
  pageSize: number;
  folderId: string | null;
}

export type OperationKind = 'copy' | 'move' | 'symlink' | 'shortcut';
export type ConflictAction = 'overwrite' | 'rename' | 'skip';

export interface ConflictItem { source: string; target: string; defaultAction: ConflictAction; }
export interface OperationPlan {
  id: string;
  kind: OperationKind;
  source: string;
  target: string;
  estimatedBytes: number;
  conflicts: ConflictItem[];
  checks: { sourceExists: boolean; targetParentWritable: boolean; enoughSpace: boolean };
}
export interface OperationResult { id: string; success: boolean; message: string; changedPaths: string[]; rollbackAvailable: boolean; }
export interface RepkgJob { id: string; inputPath: string; outputPath: string; status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'; progress: number; error?: string; }
export interface ImportFileRequest { inputPath: string; managedDirectory: string; title: string; mode: 'copy' | 'move' | 'link'; previewPath?: string; }

export interface LibraryQuery { filter: FilterState; }
export interface LibraryPage { items: ProjectRecord[]; total: number; page: number; pageCount: number; }

export interface TaskEvent { taskId: string; kind: 'scan' | 'operation' | 'repkg'; status: string; progress: number; message?: string; }

export interface RemakeApi {
  settings: { get(): Promise<AppSettings>; update(patch: Partial<AppSettings>): Promise<AppSettings>; reset(): Promise<AppSettings>; detectPaths(): Promise<Partial<AppSettings>>; pickDirectory(defaultPath?: string): Promise<string | null>; pickFile(filters?: { name: string; extensions: string[] }[]): Promise<string | null>; };
  library: { scan(): Promise<{ taskId: string }>; list(query: LibraryQuery): Promise<LibraryPage>; get(id: string): Promise<ProjectRecord | null>; folders(): Promise<FolderNode[]>; getThumbnail(path: string): Promise<string | null>; updateMetadata(id: string, patch: Pick<ProjectRecord, 'title' | 'description' | 'favorite' | 'tags'>): Promise<ProjectRecord>; recalculateSize(id: string): Promise<ProjectRecord>; importFile(request: ImportFileRequest): Promise<ProjectRecord>; openPath(path: string): Promise<void>; };
  operations: { preview(input: Omit<OperationPlan, 'id' | 'estimatedBytes' | 'conflicts' | 'checks'>): Promise<OperationPlan>; execute(plan: OperationPlan, actions: Record<string, ConflictAction>): Promise<OperationResult>; cancel(id: string): Promise<boolean>; getLog(id: string): Promise<OperationResult | null>; };
  storage: { createSymlink(source: string, target: string): Promise<OperationResult>; restoreSymlink(linkPath: string, backupPath: string): Promise<OperationResult>; createShortcut(shortcutPath: string, targetPath: string): Promise<OperationResult>; createShortcutBatch(sourceDirectory: string, targetDirectory: string): Promise<OperationResult[]>; };
  repkg: { start(inputPath: string): Promise<RepkgJob>; cancel(id: string): Promise<boolean>; getOutput(id: string): Promise<string[]>; };
  diagnostics: { getEnvironment(): Promise<Record<string, string>>; };
  onTaskEvent(handler: (event: TaskEvent) => void): () => void;
}
