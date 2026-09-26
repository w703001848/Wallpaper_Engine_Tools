/** Ensures old project indexes gain NAS metadata without losing existing rows. */
import { DatabaseSync } from "node:sqlite";
import { describe, expect, it } from "vitest";
import { ensureProjectStoragePathColumn } from "../electron/database.js";

describe("database migration", () => {
  it("adds storage_path to an existing projects table", () => {
    const db = new DatabaseSync(":memory:");
    db.exec(
      "CREATE TABLE projects (id TEXT PRIMARY KEY, title TEXT); INSERT INTO projects VALUES ('1', 'Demo')",
    );
    ensureProjectStoragePathColumn(db);
    const columns = db.prepare("PRAGMA table_info(projects)").all() as {
      name: string;
    }[];
    expect(columns.map((column) => column.name)).toContain("storage_path");
    expect(
      db.prepare("SELECT storage_path FROM projects WHERE id = ?").get("1"),
    ).toMatchObject({ storage_path: "" });
    db.close();
  });
});
