/** Persists storage-page activity for the current application session. */
import fs from "node:fs/promises";
import path from "node:path";
import { app } from "electron";

export type StorageLogKind = "info" | "success" | "error";

export function storageLogPath(baseDirectory = app.getPath("userData")): string {
  return path.join(baseDirectory, "storage.log");
}

export async function clearStorageLog(
  filePath = storageLogPath(),
): Promise<void> {
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, "", "utf8");
}

export async function appendStorageLog(
  message: string,
  kind: StorageLogKind = "info",
  filePath = storageLogPath(),
): Promise<void> {
  const cleanMessage = message.replace(/[\r\n]+/g, " ").trim();
  if (!cleanMessage) return;
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.appendFile(
    filePath,
    `${new Date().toISOString()} [${kind}] ${cleanMessage}\n`,
    "utf8",
  );
}
