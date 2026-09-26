import { describe, expect, it } from "vitest";
import path from "node:path";
import fs from "node:fs/promises";
import os from "node:os";
import { scanSource } from "../electron/scanner.js";

describe("scanner", () => {
  it("normalizes a project and marks missing project.json", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-remake-"));
    const valid = path.join(root, "123");
    const invalid = path.join(root, "missing");
    const marked = path.join(root, "marked");
    const shortcutShell = path.join(root, "shortcut-shell");
    await fs.mkdir(valid);
    await fs.mkdir(invalid);
    await fs.mkdir(marked);
    await fs.mkdir(shortcutShell);
    await fs.writeFile(
      path.join(valid, "project.json"),
      JSON.stringify({
        title: "Demo",
        type: "scene",
        preview: "preview.jpg",
        storagepath: "\\\\server\\share\\123",
        filesize: 123456,
        subscriptiondate: 1700000000,
        updatedate: 1700000100,
        tags: ["a"],
      }),
    );
    await fs.writeFile(path.join(valid, "preview.jpg"), "image");
    await fs.writeFile(
      path.join(marked, "project.json"),
      JSON.stringify({
        title: "Marked",
        type: "video",
        invalid: true,
        status: "invalid",
      }),
    );
    await fs.writeFile(
      path.join(shortcutShell, "project.json"),
      JSON.stringify({ title: "Shortcut shell", type: "video" }),
    );
    await fs.writeFile(path.join(shortcutShell, "shortcut-shell.lnk"), "link");
    const rows = await scanSource({
      id: "t",
      name: "Test",
      kind: "backup",
      path: root,
      enabled: true,
    });
    expect(rows).toHaveLength(4);
    expect(rows.find((row) => row.title === "Demo")?.previewPath).toBe(
      path.join(valid, "preview.jpg"),
    );
    expect(rows.find((row) => row.title === "Demo")?.storagePath).toBe(
      "\\\\server\\share\\123",
    );
    expect(rows.find((row) => row.title === "Demo")?.source).toBe("nas");
    expect(rows.find((row) => row.title === "Shortcut shell")?.source).toBe(
      "nas",
    );
    expect(rows.find((row) => row.title === "Marked")?.source).toBe("backup");
    expect(rows.find((row) => row.title === "Demo")?.fileSize).toBe(123456);
    expect(rows.find((row) => row.title === "Demo")?.updatedAt).toBe(
      1700000100000,
    );
    expect(rows.find((row) => row.title === "Demo")?.subscriptionDate).toBe(
      1700000000000,
    );
    expect(rows.find((row) => row.rootPath === invalid)?.fileSize).toBe(0);
    expect(rows.find((row) => row.rootPath === invalid)?.missingProject).toBe(
      true,
    );
    expect(rows.find((row) => row.rootPath === invalid)?.invalid).toBe(true);
    expect(rows.find((row) => row.rootPath === marked)?.invalid).toBe(false);
    await fs.rm(root, { recursive: true, force: true });
  });

  it("inherits a missing type from the dependency project", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-dependency-"));
    const child = path.join(root, "100-child");
    const explicit = path.join(root, "200-explicit");
    const missingParent = path.join(root, "300-missing-parent");
    const parent = path.join(root, "900-parent");
    await Promise.all([
      fs.mkdir(child),
      fs.mkdir(explicit),
      fs.mkdir(missingParent),
      fs.mkdir(parent),
    ]);
    await Promise.all([
      fs.writeFile(
        path.join(child, "project.json"),
        JSON.stringify({ title: "Child", dependency: "900" }),
      ),
      fs.writeFile(
        path.join(explicit, "project.json"),
        JSON.stringify({
          title: "Explicit",
          type: "web",
          dependency: "900-parent",
        }),
      ),
      fs.writeFile(
        path.join(missingParent, "project.json"),
        JSON.stringify({ title: "Missing parent", dependency: "not-found" }),
      ),
      fs.writeFile(
        path.join(parent, "project.json"),
        JSON.stringify({ title: "Parent", workshopid: 900, type: "scene" }),
      ),
    ]);

    const rows = await scanSource({
      id: "dependency",
      name: "Dependency",
      kind: "workshop",
      path: root,
      enabled: true,
    });

    expect(rows.find((row) => row.title === "Child")?.type).toBe("scene");
    expect(rows.find((row) => row.title === "Explicit")?.type).toBe("web");
    expect(rows.find((row) => row.title === "Missing parent")?.type).toBe(
      "unknown",
    );
    await fs.rm(root, { recursive: true, force: true });
  });

  it("marks workshop directories missing from workshopcache as invalid", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-workshop-"));
    const cached = path.join(root, "100");
    const uncached = path.join(root, "200");
    const metadataFile = path.join(root, "workshopcache.json");
    await Promise.all([fs.mkdir(cached), fs.mkdir(uncached)]);
    await Promise.all([
      fs.writeFile(
        path.join(cached, "project.json"),
        JSON.stringify({ title: "Cached", type: "video", filesize: 1 }),
      ),
      fs.writeFile(
        path.join(uncached, "project.json"),
        JSON.stringify({ title: "Uncached", type: "video", filesize: 1 }),
      ),
      fs.writeFile(
        metadataFile,
        JSON.stringify({ wallpapers: [{ workshopid: 100 }] }),
      ),
    ]);

    const rows = await scanSource({
      id: "workshop",
      name: "Workshop",
      kind: "workshop",
      path: root,
      enabled: true,
      metadataFile,
    });

    expect(rows.find((row) => row.workshopId === "100")?.invalid).toBe(false);
    expect(rows.find((row) => row.workshopId === "200")?.invalid).toBe(true);
    expect(rows.find((row) => row.workshopId === "200")?.missingProject).toBe(
      false,
    );
    await fs.rm(root, { recursive: true, force: true });
  });

  it("calculates and persists capacity when filesize is missing", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-capacity-"));
    const missingSize = path.join(root, "missing-size");
    const cachedSize = path.join(root, "cached-size");
    await Promise.all([fs.mkdir(missingSize), fs.mkdir(cachedSize)]);
    const missingProjectPath = path.join(missingSize, "project.json");
    await fs.writeFile(
      missingProjectPath,
      JSON.stringify({ title: "Missing size", type: "scene" }),
    );
    await fs.writeFile(path.join(missingSize, "asset.bin"), "asset");
    await fs.writeFile(
      path.join(cachedSize, "project.json"),
      JSON.stringify({ title: "Cached size", type: "scene", filesize: 42 }),
    );
    const metadataFile = path.join(root, "workshopcache.json");
    await fs.writeFile(
      metadataFile,
      JSON.stringify({
        wallpapers: [{ workshopid: "missing-size", filesize: 999 }],
      }),
    );

    const before = await fs.stat(missingProjectPath);
    const rows = await scanSource({
      id: "capacity",
      name: "Capacity",
      kind: "backup",
      path: root,
      enabled: true,
      metadataFile,
    });

    const calculated = before.size + 5;
    expect(rows.find((row) => row.title === "Missing size")?.fileSize).toBe(
      calculated,
    );
    expect(rows.find((row) => row.title === "Cached size")?.fileSize).toBe(42);
    const manifest = JSON.parse(await fs.readFile(missingProjectPath, "utf8"));
    expect(manifest).toMatchObject({
      filesize: calculated,
      filesizelabel: `${calculated} B`,
    });
    await fs.rm(root, { recursive: true, force: true });
  });
});
