/** Creates a managed Wallpaper Engine project from one local file without touching legacy data. */
import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import type {
  ImportFileRequest,
  ProjectRecord,
  ProjectType,
} from "../src/shared/types.js";
import { formatFileSize } from "../src/shared/file-size.js";
import { createShortcut } from "./operations.js";
import { projectTypeForAsset } from "./project-asset.js";

const safeName = (value: string) => {
  const normalized = value.replace(/[<>:"/\\|?*\x00-\x1f]/g, "_").trim();
  // Dot segments would make path.join escape the managed directory.
  return normalized && normalized !== "." && normalized !== ".."
    ? normalized
    : "未命名项目";
};
/** Converts a local static image through Electron's decoder; animated GIF remains lossless and animated. */
async function prepareLocalPreview(source: string): Promise<{ name: string; bytes: Uint8Array }> {
  const extension = path.extname(source).toLowerCase();
  if (extension === ".gif") {
    return { name: "preview.gif", bytes: await fs.readFile(source) };
  }
  const { nativeImage } = await import("electron");
  try {
    const image = nativeImage.createFromPath(source);
    if (image.isEmpty()) throw new Error("无法解析本地预览图片");
    return { name: "preview.jpg", bytes: image.toJPEG(88) };
  } catch (error) {
    if (error instanceof Error && error.message.includes("无法解析")) throw error;
    throw new Error("无法读取本地预览图片");
  }
}
async function nextDirectory(root: string, name: string): Promise<string> {
  let candidate = path.join(root, name);
  let n = 1;
  while (true) {
    try {
      await fs.access(candidate);
      candidate = path.join(root, `${name} (${n++})`);
    } catch {
      return candidate;
    }
  }
}
type PreviewCreator = (source: string, output: string) => Promise<void>;
const createVideoPreview: PreviewCreator = async (source, output) => {
  const { nativeImage } = await import("electron");
  const image = await nativeImage.createThumbnailFromPath(source, {
    width: 512,
    height: 288,
  });
  if (image.isEmpty())
    throw new Error("无法从视频提取缩略图，请确认系统支持该视频编码");
  await fs.writeFile(output, image.toJPEG(88));
};

async function restoreMovedInput(
  projectFile: string,
  input: string,
  expectedSize: number,
): Promise<void> {
  try {
    await fs.rename(projectFile, input);
    return;
  } catch (error: unknown) {
    if ((error as NodeJS.ErrnoException).code !== "EXDEV") {
      try {
        await fs.access(input);
        throw new Error("原路径已被占用");
      } catch (accessError: unknown) {
        if ((accessError as NodeJS.ErrnoException).code !== "ENOENT")
          throw accessError;
      }
    }
  }
  await fs.copyFile(projectFile, input);
  if ((await fs.stat(input)).size !== expectedSize)
    throw new Error("恢复后的源文件大小不一致");
  await fs.unlink(projectFile);
}

export function createWallpaperProject(
  title: string,
  type: ProjectType,
  file: string,
  fileSize: number,
  timestamp: number,
  preview?: string,
): Record<string, unknown> {
  // Wallpaper Engine resolves the selected asset relative to project.json.
  return completeWallpaperProject(
    {
      file,
      ...(preview ? { preview } : {}),
      title,
      type,
      version: 0,
    },
    fileSize,
    timestamp,
  );
}

export function completeWallpaperProject(
  data: Record<string, unknown>,
  fileSize: number,
  timestamp: number,
): Record<string, unknown> {
  // Archive shells can originate from sparse manifests, so keep existing metadata while filling the stable browser fields.
  const subscriptionDate = Number(data.subscriptiondate);
  const updateDate = Number(data.updatedate);
  return {
    contentrating: "",
    description: "",
    general: {
      properties: {
        schemecolor: {
          order: 0,
          text: "ui_browse_properties_scheme_color",
          type: "color",
          value: "0.2 0.2 0.2",
        },
      },
    },
    ratingsex: "",
    ratingviolence: "",
    version: 0,
    allowmobileupload: false,
    authorsteamid: "",
    favorite: true,
    hasrating: false,
    ispreset: false,
    local: false,
    official: false,
    rating: 0,
    ratingrounded: 5.0,
    status: "",
    workshopid: "",
    workshopurl: "",
    storagepath: "",
    ...data,
    tags: Array.isArray(data.tags) ? data.tags : [],
    filesize: fileSize,
    filesizelabel: formatFileSize(fileSize),
    subscriptiondate:
      Number.isFinite(subscriptionDate) && subscriptionDate > 0
        ? subscriptionDate
        : timestamp,
    updatedate:
      Number.isFinite(updateDate) && updateDate > 0 ? updateDate : timestamp,
  };
}

export async function updateWallpaperProjectSize(
  projectPath: string,
  fileSize: number,
  timestamp = Math.floor(Date.now() / 1000),
  projectFile?: string,
): Promise<void> {
  const data = JSON.parse(await fs.readFile(projectPath, "utf8")) as Record<
    string,
    unknown
  >;
  const temporary = `${projectPath}.tmp`;
  try {
    // Replace atomically so an interrupted recalculation cannot leave a truncated manifest.
    await fs.writeFile(
      temporary,
      JSON.stringify(
        {
          ...data,
          ...(projectFile ? { file: projectFile } : {}),
          filesize: fileSize,
          filesizelabel: formatFileSize(fileSize),
          updatedate: timestamp,
        },
        null,
        2,
      ),
      "utf8",
    );
    await fs.rename(temporary, projectPath);
  } catch (error) {
    await fs.rm(temporary, { force: true }).catch(() => undefined);
    throw error;
  }
}

export async function importSingleFile(
  request: ImportFileRequest,
  previewCreator: PreviewCreator = createVideoPreview,
): Promise<ProjectRecord> {
  const input = path.resolve(request.inputPath);
  const shortcutTarget = request.shortcutTargetPath
    ? path.win32.normalize(request.shortcutTargetPath)
    : input;
  const managed = path.resolve(request.managedDirectory);
  const inputStat = await fs.stat(input);
  if (!inputStat.isFile()) throw new Error("导入源必须是文件");
  const type = projectTypeForAsset(input);
  const base = path.basename(input);
  const title = request.title?.trim() || path.parse(base).name;
  await fs.mkdir(managed, { recursive: true });
  const root = await nextDirectory(managed, safeName(title));
  await fs.mkdir(root);
  // Keep the imported file untouched; the application manifest uses a stable upload field below.
  let assetName = base;
  let projectFile = path.join(root, assetName);
  let movedInput = false;
  try {
    if (request.mode === "copy") await fs.copyFile(input, projectFile);
    else if (request.mode === "move") {
      try {
        await fs.rename(input, projectFile);
      } catch (error: unknown) {
        if ((error as NodeJS.ErrnoException).code !== "EXDEV") throw error;
        await fs.copyFile(input, projectFile);
        if ((await fs.stat(projectFile)).size !== inputStat.size)
          throw new Error("跨磁盘移动校验失败");
        await fs.unlink(input);
      }
      movedInput = true;
    }
    else {
      assetName = `${path.parse(base).name}.lnk`;
      projectFile = path.join(root, assetName);
      const shortcut = await createShortcut(projectFile, shortcutTarget);
      if (!shortcut.success) throw new Error(shortcut.message);
    }
    let preview = "";
    if (request.previewPath) {
      const localPreview = await prepareLocalPreview(request.previewPath);
      preview = localPreview.name;
      await fs.writeFile(path.join(root, preview), localPreview.bytes);
    } else if (type === "video") {
      preview = "preview.jpg";
      // A shortcut has no video frames, so link mode extracts the preview from its original target.
      await previewCreator(
        request.mode === "link" ? input : projectFile,
        path.join(root, preview),
      );
    }
    const now = Date.now();
    const timestamp = Math.floor(now / 1000);
    const data = createWallpaperProject(
      title,
      type,
      // The manifest is portable: never persist the source machine's absolute path.
      type === "application" ? "上传用.exe" : assetName,
      inputStat.size,
      timestamp,
      preview,
    );
    const projectPath = path.join(root, "project.json");
    await fs.writeFile(
      `${projectPath}.tmp`,
      JSON.stringify(data, null, 2),
      "utf8",
    );
    await fs.rename(`${projectPath}.tmp`, projectPath);
    return {
      id: crypto.createHash("sha1").update(`backup:${root}`).digest("hex"),
      workshopId: path.basename(root),
      title,
      type,
      source: "backup",
      rootPath: root,
      projectPath,
      previewPath: preview ? path.join(root, preview) : null,
      storagePath: "",
      description: "",
      authorSteamId: "",
      fileSize: inputStat.size,
      updatedAt: now,
      subscriptionDate: now,
      invalid: false,
      missingProject: false,
      favorite: true,
      tags: [],
    };
  } catch (error) {
    if (movedInput) {
      // Thumbnail or manifest failures happen after the move, so restore the source before removing partial output.
      try {
        await restoreMovedInput(projectFile, input, inputStat.size);
      } catch (rollbackError) {
        throw new Error(
          `${error instanceof Error ? error.message : String(error)}；源文件恢复失败，文件保留在 ${projectFile}：${rollbackError instanceof Error ? rollbackError.message : String(rollbackError)}`,
        );
      }
    }
    await fs.rm(root, { recursive: true, force: true });
    throw error;
  }
}
