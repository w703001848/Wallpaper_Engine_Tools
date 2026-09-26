/** Verifies metadata edits update both the local shell and the archived NAS manifest. */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import {
  readProjectManifest,
  writeProjectManifests,
} from "../electron/project-sync.js";
import type { ProjectRecord } from "../src/shared/types.js";

describe("project manifest synchronization", () => {
  it("writes metadata to the shell and NAS while preserving each file path", async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), "wet-sync-"));
    try {
      const shell = path.join(fixture, "shell");
      const storage = path.join(fixture, "nas");
      await Promise.all([fs.mkdir(shell), fs.mkdir(storage)]);
      const shellProject = path.join(shell, "project.json");
      const remoteProject = path.join(storage, "project.json");
      await fs.writeFile(
        shellProject,
        JSON.stringify({
          file: path.join(storage, "scene.json"),
          storagepath: storage,
          title: "旧标题",
          description: "旧描述",
        }),
        "utf8",
      );
      await fs.writeFile(
        remoteProject,
        JSON.stringify({
          file: "scene.json",
          storagepath: storage,
          title: "旧标题",
          description: "旧描述",
        }),
        "utf8",
      );
      const project = {
        id: "shell-1",
        workshopId: "1",
        title: "旧标题",
        type: "scene",
        source: "backup",
        rootPath: shell,
        projectPath: shellProject,
        previewPath: null,
        storagePath: storage,
        description: "旧描述",
        authorSteamId: "",
        fileSize: 0,
        updatedAt: 0,
        subscriptionDate: 0,
        invalid: false,
        missingProject: false,
        favorite: false,
        tags: [],
      } satisfies ProjectRecord;

      await writeProjectManifests(project, await readProjectManifest(shellProject), {
        title: "新标题",
        description: "新描述",
        favorite: true,
        tags: ["同步"],
        updatedate: 1_700_000_000,
      });
      const shellManifest = JSON.parse(await fs.readFile(shellProject, "utf8"));
      const remoteManifest = JSON.parse(await fs.readFile(remoteProject, "utf8"));
      expect(shellManifest).toMatchObject({
        title: "新标题",
        description: "新描述",
        favorite: true,
        tags: ["同步"],
        file: path.join(storage, "scene.json"),
      });
      expect(remoteManifest).toMatchObject({
        title: "新标题",
        description: "新描述",
        favorite: true,
        tags: ["同步"],
        file: "scene.json",
      });
    } finally {
      await fs.rm(fixture, { recursive: true, force: true });
    }
  });
});
