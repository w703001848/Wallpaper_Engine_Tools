/** Tests cache invalidation when configured source roots change or are disabled. */
import path from "node:path";
import { describe, expect, it } from "vitest";
import { projectBelongsToSources } from "../electron/source-matching.js";
import type { ProjectRecord, SourceConfig } from "../src/shared/types.js";

const project = (
  source: ProjectRecord["source"],
  rootPath: string,
  storagePath = "",
): ProjectRecord => ({
  id: rootPath,
  workshopId: "",
  title: "",
  type: "unknown",
  source,
  rootPath,
  projectPath: path.join(rootPath, "project.json"),
  previewPath: null,
  storagePath,
  description: "",
  authorSteamId: "",
  fileSize: 0,
  updatedAt: 0,
  subscriptionDate: 0,
  invalid: false,
  missingProject: false,
  favorite: false,
  tags: [],
});
const source = (
  id: string,
  kind: SourceConfig["kind"],
  sourcePath: string,
  enabled = true,
): SourceConfig => ({ id, name: id, kind, path: sourcePath, enabled });

describe("project source matching", () => {
  it("drops projects from the previous backup directory", () => {
    const active = [source("backup", "backup", "D:\\wallpapers\\new-backup")];
    expect(
      projectBelongsToSources(
        project("backup", "D:\\wallpapers\\old-backup\\100"),
        active,
      ),
    ).toBe(false);
    expect(
      projectBelongsToSources(
        project("backup", "D:\\wallpapers\\new-backup\\100"),
        active,
      ),
    ).toBe(true);
  });

  it("drops projects when their temporary source is disabled", () => {
    const disabled = [source("temp", "temp", "D:\\wallpapers\\temp", false)];
    expect(
      projectBelongsToSources(
        project("temp", "D:\\wallpapers\\temp\\100"),
        disabled,
      ),
    ).toBe(false);
  });

  it("keeps NAS shells owned by the active backup directory", () => {
    const active = [source("backup", "backup", "D:\\wallpapers\\backup")];
    expect(
      projectBelongsToSources(
        project(
          "nas",
          "D:\\wallpapers\\backup\\100",
        ),
        active,
      ),
    ).toBe(true);
  });

  it("does not confuse sibling directories with a shared prefix", () => {
    const active = [source("temp", "temp", "D:\\wallpapers\\temp")];
    expect(
      projectBelongsToSources(
        project("temp", "D:\\wallpapers\\temp-old\\100"),
        active,
      ),
    ).toBe(false);
  });
});
