/** Verifies session log truncation and safe line-oriented persistence. */
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, expect, it } from "vitest";
import { appendStorageLog, clearStorageLog } from "../electron/storage-log.js";

describe("storage log", () => {
  it("clears the previous session before appending new entries", async () => {
    const root = await fs.mkdtemp(path.join(os.tmpdir(), "wet-storage-log-"));
    const filePath = path.join(root, "storage.log");
    try {
      await fs.writeFile(filePath, "old session\n", "utf8");
      await clearStorageLog(filePath);
      await appendStorageLog("预检通过\n目标已准备", "success", filePath);
      const content = await fs.readFile(filePath, "utf8");
      expect(content).not.toContain("old session");
      expect(content).toMatch(/\[success\] 预检通过 目标已准备\r?\n$/u);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });
});
