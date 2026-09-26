/** Verifies Windows NAS path validation and bounded location status checks. */
import { constants } from "node:fs";
import { describe, expect, it } from "vitest";
import {
  checkNasLocation,
  mappedDriveRemote,
  mappedDriveUncPath,
  nasShortcutTarget,
} from "../electron/nas-storage.js";
import { normalizeNasPath } from "../electron/settings.js";

const mapping = {
  id: "nas-1",
  name: "归档盘",
  path: "\\\\server\\share",
  enabled: true,
};

describe("NAS path validation", () => {
  it("accepts UNC and mapped drive paths", () => {
    expect(normalizeNasPath("\\\\server\\share\\archive")).toBe(
      "\\\\server\\share\\archive",
    );
    expect(normalizeNasPath("z:/wallpapers")).toBe("z:\\wallpapers");
  });

  it.each([
    "archive",
    ".\\archive",
    "ftp://server/share",
    "sftp://server/share",
    "https://server/share",
  ])("rejects unsupported path %s", (value) => {
    expect(() => normalizeNasPath(value)).toThrow();
  });

  it("builds shortcut targets from the configured IPv4 UNC root", () => {
    expect(
      nasShortcutTarget(
        "\\\\STORAGE-NAS\\share\\archive\\clips\\demo.mp4",
        [
          {
            ...mapping,
            path: "\\\\192.168.10.101\\share\\archive",
          },
        ],
      ),
    ).toBe("\\\\192.168.10.101\\share\\archive\\clips\\demo.mp4");
  });

  it("converts a mapped drive file to the configured IPv4 UNC path", () => {
    const output = [
      "Status       Local     Remote",
      "OK           Z:        \\\\192.168.10.101\\hdd0",
    ].join("\r\n");
    const remote = mappedDriveRemote(output);
    expect(remote).toBe("\\\\192.168.10.101\\hdd0");
    const unc = mappedDriveUncPath(
      "Z:\\等待删除\\videos\\demo.mp4",
      remote!,
    );
    expect(
      nasShortcutTarget(unc, [
        {
          ...mapping,
          path: "\\\\192.168.10.101\\hdd0\\等待删除",
        },
      ]),
    ).toBe("\\\\192.168.10.101\\hdd0\\等待删除\\videos\\demo.mp4");
  });

  it("leaves unrelated local files unchanged", () => {
    expect(nasShortcutTarget("D:\\videos\\demo.mp4", [mapping])).toBe(
      "D:\\videos\\demo.mp4",
    );
  });
});

describe("NAS location status", () => {
  it("reports writable when read and write checks pass", async () => {
    await expect(
      checkNasLocation(mapping, 50, async () => undefined),
    ).resolves.toMatchObject({ state: "writable" });
  });

  it("reports readonly when only the write check fails", async () => {
    const access = async (_target: string, mode: number) => {
      if (mode === constants.W_OK) throw new Error("只读");
    };
    await expect(checkNasLocation(mapping, 50, access)).resolves.toMatchObject({
      state: "readonly",
      error: "只读",
    });
  });

  it("reports offline for read failures and timeouts", async () => {
    await expect(
      checkNasLocation(mapping, 50, async () => {
        throw new Error("不可达");
      }),
    ).resolves.toMatchObject({ state: "offline", error: "不可达" });
    await expect(
      checkNasLocation(mapping, 5, () => new Promise(() => undefined)),
    ).resolves.toMatchObject({ state: "offline", error: "检测超时（5 ms）" });
  });
});
