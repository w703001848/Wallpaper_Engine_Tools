/** Versioned JSON settings. It intentionally starts clean and never mutates the legacy config.json. */
import { app } from "electron";
import fs from "node:fs/promises";
import path from "node:path";
import type {
  AppSettings,
  NasMapping,
  SourceConfig,
} from "../src/shared/types.js";

const defaults = (): AppSettings => ({
  version: 1,
  steamPath: "",
  wallpaperPath: "",
  backupPath: "",
  sources: [],
  tempDirectories: [],
  nasMappings: [],
  libraryView: {
    sources: [],
    types: [],
    sort: "updatedAt",
    descending: true,
  },
  display: {
    pageSize: 50,
    columnCount: 5,
    cardSize: "comfortable",
    theme: "dark",
  },
});

const normalizeDisplay = (
  display: Partial<AppSettings["display"]> | undefined,
): AppSettings["display"] => ({
  ...defaults().display,
  ...display,
  // Persisted settings can come from older builds or manual edits, so constrain values at the storage boundary.
  pageSize: [50, 100, 200].includes(Number(display?.pageSize))
    ? Number(display?.pageSize)
    : defaults().display.pageSize,
  columnCount: Math.min(
    10,
    Math.max(2, Math.round(Number(display?.columnCount) || defaults().display.columnCount)),
  ),
});

export const normalizeLibraryView = (
  view: Partial<AppSettings["libraryView"]> | undefined,
): AppSettings["libraryView"] => {
  const sourceValues = ["workshop", "backup", "temp", "nas", "unknown"];
  const typeValues = ["scene", "video", "web", "application", "unknown"];
  const sortValues = ["title", "updatedAt", "fileSize", "subscriptionDate"];
  // Filter persisted values because settings may come from an older build or be edited by hand.
  return {
    sources: Array.isArray(view?.sources)
      ? view.sources.filter((value) => sourceValues.includes(value))
      : [],
    types: Array.isArray(view?.types)
      ? view.types.filter((value) => typeValues.includes(value))
      : [],
    sort: sortValues.includes(String(view?.sort))
      ? (view?.sort as AppSettings["libraryView"]["sort"])
      : defaults().libraryView.sort,
    descending:
      typeof view?.descending === "boolean"
        ? view.descending
        : defaults().libraryView.descending,
  };
};

export class SettingsStore {
  private readonly filePath = path.join(
    app.getPath("userData"),
    "settings.json",
  );
  private data: AppSettings = defaults();

  async load(): Promise<AppSettings> {
    try {
      const loaded = {
        ...defaults(),
        ...JSON.parse(await fs.readFile(this.filePath, "utf8")),
      } as AppSettings;
      this.data = {
        ...loaded,
        display: normalizeDisplay(loaded.display),
        libraryView: normalizeLibraryView(loaded.libraryView),
        nasMappings: loaded.nasMappings.flatMap((mapping) => {
          try {
            return [normalizeNasMapping(mapping)];
          } catch {
            return [];
          }
        }),
      };
    } catch {
      await this.save();
    }
    return this.data;
  }
  get(): AppSettings {
    return this.data;
  }
  async update(patch: Partial<AppSettings>): Promise<AppSettings> {
    const checked: Partial<AppSettings> = {
      ...patch,
      ...(patch.display ? { display: normalizeDisplay(patch.display) } : {}),
      ...(patch.libraryView
        ? { libraryView: normalizeLibraryView(patch.libraryView) }
        : {}),
      ...(patch.nasMappings
        ? { nasMappings: patch.nasMappings.map(normalizeNasMapping) }
        : {}),
    };
    this.data = { ...this.data, ...checked };
    await this.save();
    return this.data;
  }
  async reset(): Promise<AppSettings> {
    this.data = defaults();
    await this.save();
    return this.data;
  }
  async save(): Promise<void> {
    await fs.mkdir(path.dirname(this.filePath), { recursive: true });
    await fs.writeFile(
      this.filePath,
      JSON.stringify(this.data, null, 2),
      "utf8",
    );
  }
  static source(
    id: string,
    name: string,
    kind: SourceConfig["kind"],
    pathValue: string,
  ): SourceConfig {
    return { id, name, kind, path: path.resolve(pathValue), enabled: true };
  }
}

export function normalizeNasPath(value: string): string {
  const candidate = value.trim().replaceAll("/", "\\");
  // Only UNC shares and rooted drive paths are accepted; URL schemes bypass filesystem permission checks.
  const unc = /^\\\\[^\\]+\\[^\\]+(?:\\.*)?$/u.test(candidate);
  const drive = /^[A-Za-z]:\\(?:.*)?$/u.test(candidate);
  if (!unc && !drive)
    throw new Error("NAS 路径必须是 \\\\server\\share 或 Z:\\... 格式");
  if (/^[A-Za-z][A-Za-z0-9+.-]*:/u.test(candidate) && !drive)
    throw new Error("不支持 FTP、SFTP、WebDAV 或普通 URL");
  return path.win32.normalize(candidate);
}

export function normalizeNasMapping(mapping: NasMapping): NasMapping {
  if (!mapping.id?.trim()) throw new Error("NAS 位置缺少 ID");
  if (!mapping.name?.trim()) throw new Error("NAS 位置名称不能为空");
  return {
    id: mapping.id.trim(),
    name: mapping.name.trim(),
    path: normalizeNasPath(mapping.path),
    enabled: Boolean(mapping.enabled),
  };
}
