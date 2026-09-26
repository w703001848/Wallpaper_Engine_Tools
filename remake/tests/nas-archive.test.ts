/** Exercises NAS archive commit and rollback using isolated filesystem trees. */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { afterEach, describe, expect, it } from "vitest";
import {
  commitNasStage,
  executeNasArchive,
  previewNasArchive,
  rebuildNasVideoShortcuts,
} from "../electron/nas-storage.js";
import type { LibraryDatabase } from "../electron/database.js";
import type { OperationResult, ProjectRecord } from "../src/shared/types.js";

const roots: string[] = [];
afterEach(async () => {
  await Promise.all(
    roots
      .splice(0)
      .map((root) => fs.rm(root, { recursive: true, force: true })),
  );
});

async function fixture(source: "workshop" | "backup" | "temp") {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-nas-"));
  roots.push(root);
  const backup = path.join(root, "backup");
  const workshop = path.join(root, "workshop");
  const temporary = path.join(root, "temp");
  const nas = path.join(root, "nas");
  await Promise.all([
    fs.mkdir(backup),
    fs.mkdir(workshop),
    fs.mkdir(temporary),
    fs.mkdir(nas),
  ]);
  const projectRoot = path.join(
    source === "backup" ? backup : source === "workshop" ? workshop : temporary,
    "100",
  );
  await fs.mkdir(projectRoot);
  await fs.writeFile(path.join(projectRoot, "video.mp4"), "content");
  await fs.writeFile(path.join(projectRoot, "preview.jpg"), "preview");
  await fs.writeFile(
    path.join(projectRoot, "project.json"),
    JSON.stringify({
      title: "Archive",
      type: "video",
      file: "video.mp4",
      preview: "preview.jpg",
      workshopid: "100",
    }),
  );
  const project: ProjectRecord = {
    id: `${source}-100`,
    workshopId: "100",
    title: "Archive",
    type: "video",
    source,
    rootPath: projectRoot,
    projectPath: path.join(projectRoot, "project.json"),
    previewPath: path.join(projectRoot, "preview.jpg"),
    storagePath: "",
    description: "",
    authorSteamId: "",
    fileSize: 7,
    updatedAt: 1,
    subscriptionDate: 1,
    invalid: false,
    missingProject: false,
    favorite: false,
    tags: [],
  };
  const saved: ProjectRecord[] = [];
  const operations: OperationResult[] = [];
  const shortcutTargets: string[] = [];
  const database = {
    upsertProjects: (items: ProjectRecord[]) => saved.push(...items),
    removeProject: () => undefined,
    saveOperation: (result: OperationResult) => operations.push(result),
  } as unknown as LibraryDatabase;
  const mapping = { id: "nas", name: "NAS", path: nas, enabled: true };
  const shortcut = async (
    shortcutPath: string,
    targetPath: string,
  ): Promise<OperationResult> => {
    // Windows rejects or creates unusable links for missing network targets, so archive commit must happen first.
    await fs.access(targetPath);
    shortcutTargets.push(targetPath);
    await fs.writeFile(shortcutPath, targetPath);
    return {
      id: shortcutPath,
      success: true,
      message: "ok",
      changedPaths: [shortcutPath],
      rollbackAvailable: true,
    };
  };
  return {
    backup,
    nas,
    project,
    database,
    mapping,
    saved,
    operations,
    shortcut,
    shortcutTargets,
  };
}

describe("NAS archive", () => {
  it("falls back to verified copy when an SMB server rejects directory rename", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-nas-commit-"));
    roots.push(root);
    const stage = path.join(root, "project.wet-staging");
    const target = path.join(root, "project");
    await fs.mkdir(stage);
    await fs.writeFile(path.join(stage, "content.bin"), "content");
    const denyRename = async () => {
      const error = new Error(
        "operation not permitted",
      ) as NodeJS.ErrnoException;
      error.code = "EPERM";
      throw error;
    };

    await expect(commitNasStage(stage, target, denyRename)).resolves.toBe(
      "copied",
    );
    await expect(
      fs.readFile(path.join(target, "content.bin"), "utf8"),
    ).resolves.toBe("content");
    await expect(fs.access(stage)).rejects.toThrow();
  });

  it.each(["workshop", "backup", "temp"] as const)(
    "archives a %s project and leaves a backup shell",
    async (source) => {
      const data = await fixture(source);
      const plan = await previewNasArchive(
        data.project,
        data.mapping,
        data.backup,
      );
      expect(Object.values(plan.checks).every(Boolean)).toBe(true);
      const result = await executeNasArchive(
        plan,
        "rename",
        data.project,
        data.mapping,
        data.backup,
        data.database,
        data.shortcut,
      );
      expect(result.success).toBe(true);
      expect(data.saved).toHaveLength(1);
      expect(result.project?.source).toBe("nas");
      const shell = path.join(data.backup, "100");
      const manifest = JSON.parse(
        await fs.readFile(path.join(shell, "project.json"), "utf8"),
      ) as Record<string, unknown>;
      expect(manifest.storagepath).toBe(path.join(data.nas, "100"));
      expect(manifest.file).toBe(path.join(data.nas, "100", "video.mp4"));
      expect(manifest).toMatchObject({
        ratingsex: "",
        ratingviolence: "",
        tags: [],
        contentrating: "",
        description: "",
        allowmobileupload: false,
        authorsteamid: "",
        favorite: true,
        filesize: 7,
        filesizelabel: "7 B",
        hasrating: false,
        ispreset: false,
        local: false,
        official: false,
        rating: 0,
        ratingrounded: 5,
        status: "",
        workshopurl: "",
      });
      expect(manifest.subscriptiondate).toEqual(expect.any(Number));
      expect(manifest.updatedate).toEqual(expect.any(Number));
      expect(data.saved[0].fileSize).toBe(7);
      expect(
        await fs.readFile(path.join(data.nas, "100", "video.mp4"), "utf8"),
      ).toBe("content");
      const archivedManifest = JSON.parse(
        await fs.readFile(path.join(data.nas, "100", "project.json"), "utf8"),
      ) as Record<string, unknown>;
      expect(archivedManifest.file).toBe("video.mp4");
      expect(archivedManifest.filesize).toBe(7);
      await expect(
        fs.access(path.join(shell, "preview.jpg")),
      ).resolves.toBeUndefined();
      await expect(
        fs.access(path.join(shell, "100.lnk")),
      ).resolves.toBeUndefined();
      await expect(
        fs.access(path.join(shell, "video.mp4.lnk")),
      ).resolves.toBeUndefined();
      await expect(
        fs.access(path.join(shell, "打开项目内容.lnk")),
      ).rejects.toThrow();
      expect(data.shortcutTargets).toEqual([
        path.join(data.nas, "100"),
        path.join(data.nas, "100", "video.mp4"),
      ]);
      if (source === "temp")
        await expect(fs.access(data.project.rootPath)).rejects.toThrow();
    },
  );

  it("keeps the source and cleans staging when shortcut creation fails", async () => {
    const data = await fixture("backup");
    const plan = await previewNasArchive(
      data.project,
      data.mapping,
      data.backup,
    );
    const failure = async (): Promise<OperationResult> => ({
      id: "failed",
      success: false,
      message: "mock failure",
      changedPaths: [],
      rollbackAvailable: false,
    });
    const result = await executeNasArchive(
      plan,
      "rename",
      data.project,
      data.mapping,
      data.backup,
      data.database,
      failure,
    );
    expect(result.success).toBe(false);
    await expect(
      fs.readFile(path.join(data.project.rootPath, "video.mp4"), "utf8"),
    ).resolves.toBe("content");
    await expect(fs.access(path.join(data.nas, "100"))).rejects.toThrow();
    expect(data.saved).toHaveLength(0);
  });

  it("creates shortcuts for every archived video and preserves subdirectories", async () => {
    const data = await fixture("backup");
    await fs.writeFile(path.join(data.project.rootPath, "extra.webm"), "extra");
    await fs.mkdir(path.join(data.project.rootPath, "clips"));
    await fs.writeFile(
      path.join(data.project.rootPath, "clips", "video.mp4"),
      "nested",
    );
    const plan = await previewNasArchive(
      data.project,
      data.mapping,
      data.backup,
    );
    const result = await executeNasArchive(
      plan,
      "rename",
      data.project,
      data.mapping,
      data.backup,
      data.database,
      data.shortcut,
    );

    expect(result.success, result.message).toBe(true);
    const shell = path.join(data.backup, "100");
    await expect(
      fs.access(path.join(shell, "video.mp4.lnk")),
    ).resolves.toBeUndefined();
    await expect(
      fs.access(path.join(shell, "extra.webm.lnk")),
    ).resolves.toBeUndefined();
    await expect(
      fs.access(path.join(shell, "clips", "video.mp4.lnk")),
    ).resolves.toBeUndefined();
    expect(data.shortcutTargets).toEqual([
      path.join(data.nas, "100"),
      path.join(data.nas, "100", "clips", "video.mp4"),
      path.join(data.nas, "100", "extra.webm"),
      path.join(data.nas, "100", "video.mp4"),
    ]);
  });

  it("repairs missing shortcuts for an existing NAS shell without overwriting links", async () => {
    const data = await fixture("backup");
    const archiveRoot = path.join(data.nas, "100");
    await fs.mkdir(path.join(archiveRoot, "clips"), { recursive: true });
    await fs.writeFile(path.join(archiveRoot, "video.mp4"), "main");
    await fs.writeFile(path.join(archiveRoot, "clips", "extra.mkv"), "extra");
    const existing = path.join(data.project.rootPath, "video.mp4.lnk");
    await fs.writeFile(existing, "keep-existing");
    const project = {
      ...data.project,
      storagePath: archiveRoot,
      source: "nas" as const,
    };

    const result = await rebuildNasVideoShortcuts(project, data.shortcut);

    expect(result.success, result.message).toBe(true);
    expect(result.changedPaths).toEqual([
      path.join(data.project.rootPath, "clips", "extra.mkv.lnk"),
    ]);
    await expect(fs.readFile(existing, "utf8")).resolves.toBe("keep-existing");
    await expect(
      fs.access(path.join(data.project.rootPath, "clips", "extra.mkv.lnk")),
    ).resolves.toBeUndefined();
  });

  it("blocks a temporary project when its backup shell already exists", async () => {
    const data = await fixture("temp");
    await fs.mkdir(path.join(data.backup, "100"));
    const plan = await previewNasArchive(
      data.project,
      data.mapping,
      data.backup,
    );
    expect(plan.checks.localShellAvailable).toBe(false);
  });

  it("supports rename, overwrite backup, and skip for NAS conflicts", async () => {
    const renamed = await fixture("backup");
    await fs.mkdir(path.join(renamed.nas, "100"));
    await fs.writeFile(path.join(renamed.nas, "100", "old.txt"), "old");
    const renamePlan = await previewNasArchive(
      renamed.project,
      renamed.mapping,
      renamed.backup,
    );
    const renameResult = await executeNasArchive(
      renamePlan,
      "rename",
      renamed.project,
      renamed.mapping,
      renamed.backup,
      renamed.database,
      renamed.shortcut,
    );
    expect(renameResult.success).toBe(true);
    await expect(
      fs.readFile(path.join(renamed.nas, "100 (1)", "video.mp4"), "utf8"),
    ).resolves.toBe("content");
    await expect(
      fs.access(path.join(renamed.backup, "100", "100 (1).lnk")),
    ).resolves.toBeUndefined();

    const overwritten = await fixture("backup");
    await fs.mkdir(path.join(overwritten.nas, "100"));
    await fs.writeFile(path.join(overwritten.nas, "100", "old.txt"), "old");
    const overwritePlan = await previewNasArchive(
      overwritten.project,
      overwritten.mapping,
      overwritten.backup,
    );
    const overwriteResult = await executeNasArchive(
      overwritePlan,
      "overwrite",
      overwritten.project,
      overwritten.mapping,
      overwritten.backup,
      overwritten.database,
      overwritten.shortcut,
    );
    expect(overwriteResult.success).toBe(true);
    const backupTarget = overwriteResult.changedPaths.find((item) =>
      item.includes(".wet-backup-"),
    );
    expect(backupTarget).toBeTruthy();
    await expect(
      fs.readFile(path.join(backupTarget!, "old.txt"), "utf8"),
    ).resolves.toBe("old");

    const skipped = await fixture("backup");
    await fs.mkdir(path.join(skipped.nas, "100"));
    const skipPlan = await previewNasArchive(
      skipped.project,
      skipped.mapping,
      skipped.backup,
    );
    const skipResult = await executeNasArchive(
      skipPlan,
      "skip",
      skipped.project,
      skipped.mapping,
      skipped.backup,
      skipped.database,
      skipped.shortcut,
    );
    expect(skipResult.success).toBe(false);
    await expect(fs.access(skipped.project.rootPath)).resolves.toBeUndefined();
  });
});
