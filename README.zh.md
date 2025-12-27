# GoPro 高亮片段提取器 🔧📹

这是一个小型工具（含命令行和 Tkinter GUI），用于从带有章节标记的 GoPro MP4 文件中提取“高亮”短片。脚本使用 `ffprobe` 读取章节信息，并调用 `ffmpeg` 裁剪剪辑，支持基于章节范围或以章节开始点为锚点的固定长度剪辑。

---

## 功能 ✅

- 基于 GoPro 生成的 MP4 章节提取剪辑
- 两种提取模式：
  - `anchor`：以章节开始为锚点，生成固定长度剪辑（pre + post）
  - `chapter`：使用完整章节范围，并可扩展前后缓冲
- 可按时间戳或序号命名输出文件
- 可选择重新编码（逐帧精确裁剪）或快速复制（stream copy）
- 支持目录批量处理，提供 progress_callback 以供 GUI 更新进度

---

## 运行环境要求 ⚙️

- Python 3.8 或更高（代码仅使用标准库）
- 系统工具：
  - `ffmpeg`、`ffprobe`（在 Debian/Ubuntu 上：`sudo apt install ffmpeg`）
- GUI 需要系统提供的 Tk（通常随 Python 一起安装）

> 注意：项目本身没有必须的 pip 依赖（见 `requirements.txt`，列出了可选项）。

---

## 安装 📥

1. 克隆仓库或将文件复制到本地目录。
2. 确保 `ffmpeg`/`ffprobe` 已安装并在 `PATH` 中。
3. 如需可选 Python 包，取消注释 `requirements.txt` 中对应行并运行：

```bash
pip install -r requirements.txt
```

---

## 使用 — 命令行 🔁

基本用法：

```bash
python gopro_highlight.py /path/to/video.mp4 --pre 1.0 --post 1.0
```

处理目录（非递归）：

```bash
python gopro_highlight.py /path/to/videos --outdir highlights
```

参数摘要：

- `--pre FLOAT`（默认 `1.0`）— 包含章节开始之前的秒数
- `--post FLOAT`（默认 `1.0`）— 包含章节结束之后的秒数
- `--outdir PATH`（默认 `highlights`）— 输出目录
- `--mode {chapter,anchor}`（默认 `anchor`）— 提取模式
- `--reencode` — 重新编码输出（逐帧精确）
- `--name-with-ts` — 使用 `HH-MM-SS.mmm` 时间戳命名输出
- `--recursive` — 递归子目录
- `--csv PATH` — 将创建的剪辑写入 CSV 摘要

---

## GUI — Tkinter 应用 🪟

启动 GUI：

```bash
python gopro_highlight_gui.py
```

GUI 可选择源目录、目标目录与选项（pre/post、递归、重新编码、时间戳命名），并显示处理日志与进度条。

---

## 实现说明 🧭

- 该工具主要通过调用系统上的 `ffprobe`/`ffmpeg` 完成任务，尽量避免额外的 Python 运行时依赖。
- `process_directory` 支持 `progress_callback(msg)` 或 `progress_callback(msg, percent)` 两种回调签名，便于 GUI 更新进度。
- GUI 使用 `root.after` 在主线程中安全更新界面。

---

## 常见问题与调试 ⚠️

- 找不到 `ffmpeg`：请安装 `ffmpeg` 并确保其在 `PATH` 中。
- 剪辑被截断或时间不准确（stream copy）— 尝试添加 `--reencode` 以获得逐帧精确的结果。
- GUI 进度不更新：确认传入的回调能接收 `percent` 参数（GUI 的回调签名为 `cb(msg, percent=None)`）。

---

## 打包为可执行文件（可选） 📦

使用 `pyinstaller`：

```bash
pip install pyinstaller
pyinstaller --onefile gopro_highlight.py
# 或包含 GUI： pyinstaller --onefile gopro_highlight_gui.py
```

注意：目标系统仍需安装 `ffmpeg`。

---

## 示例 🧪

- 从单个文件提取锚点剪辑（各前后各 1 秒）：

```bash
python gopro_highlight.py ~/Videos/GL010750.MP4 --pre 1.0 --post 1.0 --outdir ~/clips
```

- 处理目录并生成 CSV 摘要：

```bash
python gopro_highlight.py /path/to/base --outdir ~/clips --recursive --csv summary.csv
```

---

## 贡献与开发 🤝

欢迎提交问题或 PR。若添加新的运行时依赖，请同时更新 `requirements.txt` 并在 README 中说明用途。

---

## 许可证

请在此处添加你的许可证信息（当前仓库未指定 licence）。

---

如需我继续：
- 我可以把中文 `README.zh.md` 链接加入主 `README.md`（英文版），或者
- 我可以在仓库中加入一份简短的自动化检查用例（smoke test）来验证 `process_directory` 的基本行为。

告诉我你想要我接着做哪项。