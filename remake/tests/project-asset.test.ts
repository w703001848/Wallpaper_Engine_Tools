/** Verifies project assets follow Windows shortcut targets instead of measuring .lnk files. */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { findProjectAsset } from "../electron/project-asset.js";

describe("project asset resolution", () => {
  it("resolves a declared shortcut to its target", async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), "wet-asset-link-"));
    try {
      const target = path.join(fixture, "source", "Demo.mp4");
      const root = path.join(fixture, "project");
      const shortcut = path.join(root, "Demo.lnk");
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.mkdir(root);
      await fs.writeFile(target, "video");
      await fs.writeFile(shortcut, "shortcut");

      const asset = await findProjectAsset(root, "Demo.lnk", async (value) => {
        expect(value).toBe(shortcut);
        return target;
      });

      expect(asset).toEqual({
        targetPath: target,
        manifestFile: target,
        shortcutPath: shortcut,
      });
    } finally {
      await fs.rm(fixture, { recursive: true, force: true });
    }
  });

  it("uses a same-name shortcut when the declared local asset is absent", async () => {
    const fixture = await fs.mkdtemp(path.join(os.tmpdir(), "wet-asset-name-"));
    try {
      const target = path.join(fixture, "outside", "Movie.mp4");
      const root = path.join(fixture, "project");
      await fs.mkdir(path.dirname(target), { recursive: true });
      await fs.mkdir(root);
      await fs.writeFile(target, "video-content");
      await fs.writeFile(path.join(root, "Movie.lnk"), "shortcut");

      const asset = await findProjectAsset(root, "Movie.mp4", async () => target);

      expect(asset?.targetPath).toBe(target);
      expect(asset?.manifestFile).toBe(target);
    } finally {
      await fs.rm(fixture, { recursive: true, force: true });
    }
  });
});
