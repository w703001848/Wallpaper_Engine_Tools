/** SQLite repository for normalized project records and durable operation results. */
import { app } from "electron";
import { DatabaseSync } from "node:sqlite";
import type {
  FolderNode,
  OperationResult,
  ProjectRecord,
  SourceConfig,
} from "../src/shared/types.js";
import { projectBelongsToSources } from "./source-matching.js";

const timestampMs = (value: number) =>
  value > 0 && value < 1_000_000_000_000 ? value * 1000 : value;

export class LibraryDatabase {
  private readonly db: DatabaseSync;
  constructor() {
    this.db = new DatabaseSync(`${app.getPath("userData")}/library.sqlite`);
    this.db.exec("PRAGMA journal_mode = WAL");
    this.db.exec(
      `CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY, workshop_id TEXT, title TEXT, type TEXT, source TEXT, root_path TEXT, project_path TEXT, preview_path TEXT, description TEXT, author_steam_id TEXT, file_size INTEGER, updated_at INTEGER, subscription_date INTEGER, invalid INTEGER, missing_project INTEGER, favorite INTEGER, tags TEXT, storage_path TEXT NOT NULL DEFAULT ''); CREATE INDEX IF NOT EXISTS idx_projects_source ON projects(source); CREATE TABLE IF NOT EXISTS sources (id TEXT PRIMARY KEY, name TEXT, kind TEXT, path TEXT, enabled INTEGER, metadata_file TEXT); CREATE TABLE IF NOT EXISTS folders (id TEXT PRIMARY KEY, parent_id TEXT, title TEXT, path TEXT, project_refs TEXT); CREATE TABLE IF NOT EXISTS operations (id TEXT PRIMARY KEY, success INTEGER, message TEXT, changed_paths TEXT, rollback_available INTEGER, created_at INTEGER); CREATE TABLE IF NOT EXISTS repkg_jobs (id TEXT PRIMARY KEY, input_path TEXT, output_path TEXT, status TEXT, progress INTEGER, error TEXT);`,
    );
    ensureProjectStoragePathColumn(this.db);
  }
  upsertProjects(items: ProjectRecord[]): void {
    this.runTransaction(() => this.writeProjects(items));
  }
  replaceProjects(items: ProjectRecord[]): void {
    // A completed scan is a full snapshot, so rows for deleted folders must not survive indefinitely.
    this.runTransaction(() => {
      this.db.prepare("DELETE FROM projects").run();
      this.writeProjects(items);
    });
  }
  private writeProjects(items: ProjectRecord[]): void {
    const stmt = this.db.prepare(
      `INSERT INTO projects (id,workshop_id,title,type,source,root_path,project_path,preview_path,description,author_steam_id,file_size,updated_at,subscription_date,invalid,missing_project,favorite,tags,storage_path) VALUES (@id,@workshopId,@title,@type,@source,@rootPath,@projectPath,@previewPath,@description,@authorSteamId,@fileSize,@updatedAt,@subscriptionDate,@invalid,@missingProject,@favorite,@tags,@storagePath) ON CONFLICT(id) DO UPDATE SET title=excluded.title,type=excluded.type,source=excluded.source,root_path=excluded.root_path,project_path=excluded.project_path,preview_path=excluded.preview_path,description=excluded.description,author_steam_id=excluded.author_steam_id,file_size=excluded.file_size,updated_at=excluded.updated_at,subscription_date=excluded.subscription_date,invalid=excluded.invalid,missing_project=excluded.missing_project,favorite=excluded.favorite,tags=excluded.tags,storage_path=excluded.storage_path`,
    );
    items.forEach((row) =>
      stmt.run({
        ...row,
        tags: JSON.stringify(row.tags),
        invalid: row.invalid ? 1 : 0,
        missingProject: row.missingProject ? 1 : 0,
        favorite: row.favorite ? 1 : 0,
      }),
    );
  }
  list(): ProjectRecord[] {
    return (
      this.db.prepare("SELECT * FROM projects").all() as Record<
        string,
        unknown
      >[]
    ).map(this.fromRow);
  }
  get(id: string): ProjectRecord | null {
    const row = this.db.prepare("SELECT * FROM projects WHERE id=?").get(id) as
      | Record<string, unknown>
      | undefined;
    return row ? this.fromRow(row) : null;
  }
  removeProject(id: string): void {
    this.db.prepare("DELETE FROM projects WHERE id=?").run(id);
  }
  replaceSources(sources: SourceConfig[]): void {
    this.runTransaction(() => {
      this.db.prepare("DELETE FROM sources").run();
      const insert = this.db.prepare(
        "INSERT INTO sources VALUES (?,?,?,?,?,?)",
      );
      sources.forEach((source) =>
        insert.run(
          source.id,
          source.name,
          source.kind,
          source.path,
          source.enabled ? 1 : 0,
          source.metadataFile || null,
        ),
      );
      // Settings changes must remove stale cards immediately, before the asynchronous rescan finishes.
      const remove = this.db.prepare("DELETE FROM projects WHERE id=?");
      this.list()
        .filter((project) => !projectBelongsToSources(project, sources))
        .forEach((project) => remove.run(project.id));
    });
  }
  replaceFolders(nodes: FolderNode[]): void {
    const flat: FolderNode[] = [];
    const visit = (items: FolderNode[]) =>
      items.forEach((item) => {
        flat.push(item);
        visit(item.children);
      });
    visit(nodes);
    this.runTransaction(() => {
      this.db.prepare("DELETE FROM folders").run();
      const insert = this.db.prepare("INSERT INTO folders VALUES (?,?,?,?,?)");
      flat.forEach((node) =>
        insert.run(
          node.id,
          node.parentId,
          node.title,
          node.path,
          JSON.stringify(node.projectRefs),
        ),
      );
    });
  }
  listFolders(): FolderNode[] {
    const rows = this.db.prepare("SELECT * FROM folders").all() as Record<
      string,
      unknown
    >[];
    const map = new Map<string, FolderNode>();
    rows.forEach((row) =>
      map.set(String(row.id), {
        id: String(row.id),
        parentId: row.parent_id ? String(row.parent_id) : null,
        title: String(row.title),
        path: String(row.path),
        projectRefs: JSON.parse(String(row.project_refs || "[]")),
        children: [],
      }),
    );
    const roots: FolderNode[] = [];
    map.forEach((node) =>
      node.parentId && map.has(node.parentId)
        ? map.get(node.parentId)!.children.push(node)
        : roots.push(node),
    );
    return roots;
  }
  getFolderRefs(id: string): string[] {
    const row = this.db
      .prepare("SELECT project_refs FROM folders WHERE id=?")
      .get(id) as { project_refs: string } | undefined;
    return row ? JSON.parse(row.project_refs) : [];
  }
  updateMetadata(
    id: string,
    patch: Pick<ProjectRecord, "title" | "description" | "favorite" | "tags">,
  ): ProjectRecord {
    this.db
      .prepare(
        "UPDATE projects SET title=?,description=?,favorite=?,tags=? WHERE id=?",
      )
      .run(
        patch.title,
        patch.description,
        patch.favorite ? 1 : 0,
        JSON.stringify(patch.tags),
        id,
      );
    return this.get(id)!;
  }
  updateSize(id: string, fileSize: number): ProjectRecord {
    this.db
      .prepare("UPDATE projects SET file_size=? WHERE id=?")
      .run(fileSize, id);
    return this.get(id)!;
  }
  saveOperation(result: OperationResult): void {
    this.db
      .prepare("INSERT OR REPLACE INTO operations VALUES (?,?,?,?,?,?)")
      .run(
        result.id,
        result.success ? 1 : 0,
        result.message,
        JSON.stringify(result.changedPaths),
        result.rollbackAvailable ? 1 : 0,
        Date.now(),
      );
  }
  getOperation(id: string): OperationResult | null {
    const row = this.db
      .prepare("SELECT * FROM operations WHERE id=?")
      .get(id) as Record<string, unknown> | undefined;
    return row
      ? {
          id: String(row.id),
          success: Boolean(row.success),
          message: String(row.message),
          changedPaths: JSON.parse(String(row.changed_paths)),
          rollbackAvailable: Boolean(row.rollback_available),
        }
      : null;
  }
  reset(): void {
    this.db.exec(
      "DELETE FROM projects; DELETE FROM sources; DELETE FROM folders; DELETE FROM operations; DELETE FROM repkg_jobs;",
    );
  }
  close(): void {
    this.db.close();
  }
  private runTransaction(action: () => void): void {
    // Explicit transactions preserve the all-or-nothing replacement behavior of index batches.
    this.db.exec("BEGIN IMMEDIATE");
    try {
      action();
      this.db.exec("COMMIT");
    } catch (error) {
      this.db.exec("ROLLBACK");
      throw error;
    }
  }
  private fromRow(row: Record<string, unknown>): ProjectRecord {
    const storagePath = String(row.storage_path ?? "");
    // Older indexes stored NAS shells as backup rows; derive their UI source until the next scan persists it.
    const source =
      row.source === "backup" && storagePath ? "nas" : row.source;
    return {
      id: String(row.id),
      workshopId: String(row.workshop_id),
      title: String(row.title),
      type: row.type as ProjectRecord["type"],
      source: source as ProjectRecord["source"],
      rootPath: String(row.root_path),
      projectPath: String(row.project_path),
      previewPath: row.preview_path ? String(row.preview_path) : null,
      storagePath,
      description: String(row.description ?? ""),
      authorSteamId: String(row.author_steam_id ?? ""),
      fileSize: Number(row.file_size),
      updatedAt: Number(row.updated_at),
      subscriptionDate: timestampMs(Number(row.subscription_date)),
      invalid: Boolean(row.invalid),
      missingProject: Boolean(row.missing_project),
      favorite: Boolean(row.favorite),
      tags: JSON.parse(String(row.tags || "[]")),
    };
  }
}

export function ensureProjectStoragePathColumn(db: DatabaseSync): void {
  const columns = db.prepare("PRAGMA table_info(projects)").all() as {
    name: string;
  }[];
  // Existing databases are upgraded in place so NAS metadata survives without a destructive index reset.
  if (!columns.some((column) => column.name === "storage_path"))
    db.exec(
      "ALTER TABLE projects ADD COLUMN storage_path TEXT NOT NULL DEFAULT ''",
    );
}
