/** Verifies capacity recalculation follows NAS storage instead of measuring local shell links. */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { recalculateProjectSize } from "../electron/project-size.js";
import type { ProjectRecord } from "../src/shared/types.js";

describe("project capacity recalculation", () => {
  it("includes dependent files beside a local scene entry", async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), "wet-size-scene-"));
    try {
      const projectPath = path.join(fixture, "project.json");
      await fs.writeFile(
        projectPath,
        JSON.stringify({ file: "scene.json", filesize: 0 }),
        "utf8",
      );
      await fs.writeFile(path.join(fixture, "scene.json"), "scene", "utf8");
      await fs.writeFile(path.join(fixture, "texture.bin"), "texture", "utf8");
      const before = await fs.stat(projectPath);
      const project = {
        id: "scene-100",
        workshopId: "100",
        title: "Scene",
        type: "scene",
        source: "backup",
        rootPath: fixture,
        projectPath,
        previewPath: null,
        storagePath: "",
        description: "",
        authorSteamId: "",
        fileSize: 0,
        updatedAt: 0,
        subscriptionDate: 0,
        invalid: false,
        missingProject: false,
        favorite: false,
        tags: [],
      } satisfies ProjectRecord;

      const size = await recalculateProjectSize(project, async () => "", 1);
      expect(size).toBe(before.size + 12);
      const manifest = JSON.parse(await fs.readFile(projectPath, "utf8"));
      expect(manifest.file).toBe("scene.json");
      expect(manifest.filesize).toBe(size);
    } finally {
      await fs.rm(fixture, { recursive: true, force: true });
    }
  });

  it("measures an archived scene directory and preserves its manifest entry file", async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), "wet-size-shell-"));
    try {
      const shell = path.join(fixture, "backup", "100");
      const storage = path.join(fixture, "nas", "100");
      await Promise.all([
        fs.mkdir(shell, { recursive: true }),
        fs.mkdir(path.join(storage, "assets"), { recursive: true }),
      ]);
      const projectPath = path.join(shell, "project.json");
      await fs.writeFile(
        projectPath,
        JSON.stringify({
          file: "scene.json",
          storagepath: storage,
          filesize: 0,
          filesizelabel: "",
        }),
        "utf8",
      );
      await fs.writeFile(path.join(storage, "scene.json"), "scene", "utf8");
      await fs.writeFile(path.join(storage, "assets", "data.bin"), "content", "utf8");
      await fs.writeFile(
        path.join(storage, "project.json"),
        JSON.stringify({ file: "scene.json", storagepath: storage }),
        "utf8",
      );
      const expectedSize =
        (await fs.stat(path.join(storage, "scene.json"))).size +
        (await fs.stat(path.join(storage, "assets", "data.bin"))).size +
        (await fs.stat(path.join(storage, "project.json"))).size;
      const project = {
        id: "backup-100",
        workshopId: "100",
        title: "Scene",
        type: "scene",
        source: "backup",
        rootPath: shell,
        projectPath,
        previewPath: null,
        // Simulate a stale index: project.json remains the source of truth for an existing NAS shell.
        storagePath: "",
        description: "",
        authorSteamId: "",
        fileSize: 0,
        updatedAt: 0,
        subscriptionDate: 0,
        invalid: false,
        missingProject: false,
        favorite: false,
        tags: [],
      } satisfies ProjectRecord;

      await expect(
        recalculateProjectSize(project, async () => {
          throw new Error("NAS shells must not resolve their directory shortcut");
        }, 1_700_000_000),
      ).resolves.toBe(expectedSize);
      const manifest = JSON.parse(await fs.readFile(projectPath, "utf8"));
      expect(manifest).toMatchObject({
        file: "scene.json",
        filesize: expectedSize,
        filesizelabel: `${expectedSize} B`,
        updatedate: 1_700_000_000,
      });
      const remoteManifest = JSON.parse(
        await fs.readFile(path.join(storage, "project.json"), "utf8"),
      );
      expect(remoteManifest).toMatchObject({
        file: "scene.json",
        filesize: expectedSize,
        filesizelabel: `${expectedSize} B`,
        updatedate: 1_700_000_000,
      });
    } finally {
      await fs.rm(fixture, { recursive: true, force: true });
    }
  });
});
