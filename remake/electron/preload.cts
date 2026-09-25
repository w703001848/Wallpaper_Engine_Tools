/** Typed CommonJS preload bridge. No Node.js API crosses into the renderer. */
const { contextBridge, ipcRenderer } = require('electron') as typeof import('electron');
import type { RemakeApi, TaskEvent } from '../src/shared/types.js';

const api: RemakeApi = {
  settings: { get: () => ipcRenderer.invoke('settings.get'), update: (patch) => ipcRenderer.invoke('settings.update', patch), reset: () => ipcRenderer.invoke('settings.reset'), detectPaths: () => ipcRenderer.invoke('settings.detectPaths'), pickDirectory: (value) => ipcRenderer.invoke('settings.pickDirectory', value), pickFile: (filters) => ipcRenderer.invoke('settings.pickFile', filters) },
  library: { scan: () => ipcRenderer.invoke('library.scan'), list: (query) => ipcRenderer.invoke('library.list', query), get: (id) => ipcRenderer.invoke('library.get', id), folders: () => ipcRenderer.invoke('library.folders'), getThumbnail: (path) => ipcRenderer.invoke('library.getThumbnail', path), updateMetadata: (id, patch) => ipcRenderer.invoke('library.updateMetadata', id, patch), recalculateSize: (id) => ipcRenderer.invoke('library.recalculateSize', id), importFile: (request) => ipcRenderer.invoke('library.importFile', request), openPath: (target) => ipcRenderer.invoke('library.openPath', target) },
  operations: { preview: (input) => ipcRenderer.invoke('operations.preview', input), execute: (plan, actions) => ipcRenderer.invoke('operations.execute', plan, actions), cancel: (id) => ipcRenderer.invoke('operations.cancel', id), getLog: (id) => ipcRenderer.invoke('operations.getLog', id) },
  storage: { createSymlink: (source, target) => ipcRenderer.invoke('storage.createSymlink', source, target), restoreSymlink: (link, backup) => ipcRenderer.invoke('storage.restoreSymlink', link, backup), createShortcut: (shortcut, target) => ipcRenderer.invoke('storage.createShortcut', shortcut, target), createShortcutBatch: (source, target) => ipcRenderer.invoke('storage.createShortcutBatch', source, target) },
  repkg: { start: (input) => ipcRenderer.invoke('repkg.start', input), cancel: (id) => ipcRenderer.invoke('repkg.cancel', id), getOutput: (id) => ipcRenderer.invoke('repkg.getOutput', id) },
  diagnostics: { getEnvironment: () => ipcRenderer.invoke('diagnostics.getEnvironment') },
  onTaskEvent: (handler: (event: TaskEvent) => void) => { const listener = (_event: Electron.IpcRendererEvent, value: TaskEvent) => handler(value); ipcRenderer.on('task.event', listener); return () => ipcRenderer.removeListener('task.event', listener); },
};
contextBridge.exposeInMainWorld('remake', api);
