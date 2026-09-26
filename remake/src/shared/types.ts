/** Shared contracts between the Electron main process and React renderer. */

export type ProjectSource = "workshop" | "backup" | "temp" | "nas" | "unknown";
export type ProjectType = "scene" | "video" | "web" | "application" | "unknown";

export interface ProjectRecord {
  id: string;
  workshopId: string;
  title: string;
  type: ProjectType;
  source: ProjectSource;
  rootPath: string;
  projectPath: string;
  previewPath: string | null;
  storagePath: string;
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

export interface NasMapping {
  id: string;
  name: string;
  path: string;
  enabled: boolean;
}
export type NasLocationState = "writable" | "readonly" | "offline";
export interface NasLocationStatus {
  mappingId: string;
  state: NasLocationState;
  durationMs: number;
  error?: string;
}

export interface SourceConfig {
  id: string;
  name: string;
  kind: ProjectSource;
  path: string;
  enabled: boolean;
  metadataFile?: string;
}

export interface FolderNode {
  id: string;
  parentId: string | null;
  title: string;
  path: string;
  projectRefs: string[];
  children: FolderNode[];
}

export interface AppSettings {
  version: 1;
  steamPath: string;
  wallpaperPath: string;
  backupPath: string;
  sources: SourceConfig[];
  tempDirectories: SourceConfig[];
  nasMappings: NasMapping[];
  libraryView: {
    sources: ProjectSource[];
    types: ProjectType[];
    sort: FilterState["sort"];
    descending: boolean;
  };
  display: {
    pageSize: number;
    columnCount: number;
    cardSize: "compact" | "comfortable";
    theme: "dark" | "light";
  };
}

export interface FilterState {
  search: string;
  sources: ProjectSource[];
  types: ProjectType[];
  showInvalid: boolean;
  sort: "title" | "updatedAt" | "fileSize" | "subscriptionDate";
  descending: boolean;
  page: number;
  pageSize: number;
  folderId: string | null;
}

export type OperationKind = "copy" | "move" | "symlink" | "shortcut";
export type ConflictAction = "overwrite" | "rename" | "skip";

export interface ConflictItem {
  source: string;
  target: string;
  defaultAction: ConflictAction;
}
export interface OperationPlan {
  id: string;
  kind: OperationKind;
  source: string;
  target: string;
  estimatedBytes: number;
  conflicts: ConflictItem[];
  checks: {
    sourceExists: boolean;
    targetParentWritable: boolean;
    enoughSpace: boolean;
  };
}
export interface OperationResult {
  id: string;
  success: boolean;
  message: string;
  changedPaths: string[];
  rollbackAvailable: boolean;
}
export interface NasArchivePlan {
  id: string;
  projectId: string;
  mappingId: string;
  sourcePath: string;
  nasTargetPath: string;
  localShellPath: string;
  estimatedBytes: number;
  conflicts: ConflictItem[];
  checks: {
    eligibleSource: boolean;
    sourceExists: boolean;
    backupWritable: boolean;
    nasWritable: boolean;
    enoughSpace: boolean;
    localShellAvailable: boolean;
  };
  status: NasLocationStatus;
}
export interface NasArchiveResult extends OperationResult {
  project?: ProjectRecord;
}
export interface RepkgJob {
  id: string;
  inputPath: string;
  outputPath: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  error?: string;
}
export interface RepkgOutputDirectory {
  id: string;
  outputPath: string;
  updatedAt: number;
}
export interface ImportFileRequest {
  inputPath: string;
  managedDirectory: string;
  mode: "copy" | "move" | "link";
  /** Optional user-facing title; when omitted the source file name is used. */
  title?: string;
  previewPath?: string;
  /** Main-process override used when a NAS path must be written with its configured IP root. */
  shortcutTargetPath?: string;
}

export interface LibraryQuery {
  filter: FilterState;
}
export interface LibraryPage {
  items: ProjectRecord[];
  total: number;
  page: number;
  pageCount: number;
}

export interface TaskEvent {
  taskId: string;
  kind: "scan" | "operation" | "repkg";
  status: string;
  progress: number;
  message?: string;
}
export type StorageLogKind = "info" | "success" | "error";

export interface RemakeApi {
  settings: {
    get(): Promise<AppSettings>;
    update(patch: Partial<AppSettings>): Promise<AppSettings>;
    reset(): Promise<AppSettings>;
    detectPaths(): Promise<Partial<AppSettings>>;
    pickDirectory(defaultPath?: string): Promise<string | null>;
    pickFile(
      filters?: { name: string; extensions: string[] }[],
    ): Promise<string | null>;
  };
  library: {
    scan(): Promise<{ taskId: string }>;
    list(query: LibraryQuery): Promise<LibraryPage>;
    get(id: string): Promise<ProjectRecord | null>;
    folders(): Promise<FolderNode[]>;
    getThumbnail(path: string): Promise<string | null>;
    updateMetadata(
      id: string,
      patch: Pick<ProjectRecord, "title" | "description" | "favorite" | "tags">,
    ): Promise<ProjectRecord>;
    recalculateSize(id: string): Promise<ProjectRecord>;
    importFile(request: ImportFileRequest): Promise<ProjectRecord>;
    relocateAfterMove(
      id: string,
      newRootPath: string,
      destination: "backup" | "temp",
    ): Promise<ProjectRecord>;
    copyText(text: string): Promise<void>;
    openPath(path: string): Promise<void>;
    getPathForFile(file: File): string;
  };
  operations: {
    preview(
      input: Omit<
        OperationPlan,
        "id" | "estimatedBytes" | "conflicts" | "checks"
      >,
    ): Promise<OperationPlan>;
    execute(
      plan: OperationPlan,
      actions: Record<string, ConflictAction>,
    ): Promise<OperationResult>;
    cancel(id: string): Promise<boolean>;
    getLog(id: string): Promise<OperationResult | null>;
  };
  storage: {
    createSymlink(source: string, target: string): Promise<OperationResult>;
    restoreSymlink(
      linkPath: string,
      backupPath: string,
    ): Promise<OperationResult>;
    createShortcut(
      shortcutPath: string,
      targetPath: string,
    ): Promise<OperationResult>;
    createShortcutBatch(
      sourceDirectory: string,
      targetDirectory: string,
    ): Promise<OperationResult[]>;
    checkNasLocations(): Promise<NasLocationStatus[]>;
    previewNasArchive(
      projectId: string,
      mappingId: string,
    ): Promise<NasArchivePlan>;
    executeNasArchive(
      plan: NasArchivePlan,
      action: ConflictAction,
    ): Promise<NasArchiveResult>;
    rebuildNasShortcuts(projectId: string): Promise<OperationResult>;
    appendLog(message: string, kind?: StorageLogKind): Promise<void>;
  };
  repkg: {
    start(inputPath: string): Promise<RepkgJob>;
    cancel(id: string): Promise<boolean>;
    getOutput(id: string): Promise<string[]>;
    listHistory(): Promise<RepkgOutputDirectory[]>;
    deleteOutput(id: string): Promise<boolean>;
    getPathForFile(file: File): string;
  };
  diagnostics: { getEnvironment(): Promise<Record<string, string>> };
  onTaskEvent(handler: (event: TaskEvent) => void): () => void;
}
