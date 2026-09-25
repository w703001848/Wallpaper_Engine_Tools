# Wallpaper Engine Tools 重制版

这是旧版工具旁边的独立 Electron + React + TypeScript 实现，首版只支持 Windows 便携运行。

运行环境要求 Node.js 24 或更高版本。项目使用 Node/Electron 内置的 `node:sqlite`，不需要 Python、`node-gyp` 或额外 SQLite 原生模块。

## 开发

```powershell
pnpm install
pnpm dev
```

`pnpm dev` 会先生成 `dist-electron/electron/main.js` 和 `preload.cjs`，再启动主进程监听、Vite 和 Electron。首次下载 Electron 后如曾出现入口文件不存在，请停止旧进程并重新运行该命令。

## 检查

```powershell
pnpm lint
pnpm test
pnpm build
```

首次启动不会读取根目录旧版 `config.json`。设置、SQLite 索引和日志写入 Electron 的用户数据目录；旧版文件保持不变。

## 文件操作边界

- 迁移先生成预览计划，检查冲突、权限、磁盘空间和目标校验，再提交。
- 默认不覆盖已有目标；覆盖时会先生成带任务 ID 的临时备份。
- 符号链接失败不会自动复制，原目录会保留为 `.wet-backup` 以便恢复。
- 单文件项目默认保留源文件，并在受管目录生成 Windows 快捷方式。
- RePKG 每次使用独立输出目录，不清理其他任务。
