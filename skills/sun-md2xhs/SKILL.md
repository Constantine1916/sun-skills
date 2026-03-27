---
name: sun-md2xhs
description: 将 Markdown 文章转换为小红书长文图片卡片序列。每张图片带有用户自定义头像、蓝 V 认证标志和日期，仿照小红书原生帖子样式（白底、PingFang 字体），精确按内容高度裁切无空白。支持头像 URL、本地文件或自动生成默认头像。当用户说"转成小红书图片"、"生成长文卡片"、"把这篇文章转图片"、"md转小红书"、"生成小红书长文图"时触发此 skill。
---

# sun-md2xhs

将 Markdown 文章转换为小红书风格的长文图片卡片序列。

## 首次使用：初始化配置

运行一次 `--init` 将头像和名称保存到 `~/.md2xhsrc`，之后无需重复填写：

```bash
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts --init \
  --name "SUN AI" \
  --avatar /path/to/avatar.jpg
```

成功后输出：
```
✓ Config saved to ~/.md2xhsrc
  name:   SUN AI
  avatar: /path/to/avatar.jpg
```

### 头像选项

| 头像类型 | 示例 | 说明 |
|---------|------|------|
| 本地文件 | `--avatar /path/to/avatar.jpg` | 本地图片文件路径 |
| 网络URL | `--avatar https://example.com/avatar.png` | 直接使用网络图片 |
| 默认头像 | `--avatar default` | 自动用名字首字母生成 |

## 日常使用

初始化后，只需传入 MD 文件即可：

```bash
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts <input.md> --out <输出目录>
```

**示例：**
```bash
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts ~/Downloads/article.md \
  --out ~/Desktop/xhs-output/
```

## 参数说明

| 参数 | 说明 | 是否必填 |
|------|------|--------|
| `--init` | 初始化模式，保存配置到 `~/.md2xhsrc` | 首次使用 |
| `--name <name>` | 显示名称 | 与 --avatar 至少一个 |
| `--avatar <path>` | 头像：本地路径、URL、或 `default` | 与 --name 至少一个 |
| `--out <dir>` | 输出目录 | 否，默认 `./output` |
| `--date <date>` | 日期字符串（如 `2026年03月25日`） | 否，默认今天 |
| `--width <px>` | 卡片宽度（px） | 否，默认 `1080` |
| `--chrome <path>` | 指定 Chrome/Chromium 路径 | 否，自动检测 |

### 头像使用技巧

```bash
# 方式1: 用名字首字母自动生成（最简单）
bun md2xhs.ts article.md --name "AI观察家" --avatar default

# 方式2: 直接用头像URL（适合远程图片）
bun md2xhs.ts article.md --name "AI观察家" --avatar https://example.com/avatar.png

# 方式3: 本地文件（需要先上传到服务器）
bun md2xhs.ts article.md --name "AI观察家" --avatar /root/avatar.jpg
```

## 多平台支持

脚本自动检测以下位置的 Chrome/Chromium：

| 平台 | 检测路径 |
|------|---------|
| macOS | `/Applications/Google Chrome.app/...`, Chromium, Chrome Canary |
| Linux | `/usr/bin/google-chrome`, `/usr/bin/chromium`, `/snap/bin/chromium` |
| Windows | `C:\Program Files\Google\Chrome\...\chrome.exe` |

同时会扫描 PATH 环境变量中的 `google-chrome`、`chromium`、`chrome.exe` 等命令。

如需手动指定：
```bash
bun md2xhs.ts article.md --chrome /usr/bin/chromium
```

## 依赖安装

首次使用前需安装依赖：

```bash
cd ~/.claude/skills/sun-md2xhs/scripts
bun install
```

需要系统安装 Chrome/Chromium：
- macOS: [下载 Chrome](https://www.google.com/chrome/)
- Ubuntu/Debian: `sudo apt install chromium-browser`
- Fedora: `sudo dnf install chromium`
- Arch: `sudo pacman -S chromium`
- Windows: [下载 Chrome](https://www.google.com/chrome/)

## 输出结构

```
<out-dir>/
  <filename>-01.png   ← 第 1 页
  <filename>-02.png   ← 第 2 页
  ...
  .tmp-html/          ← 中间 HTML 文件（可忽略）
```

## Markdown 支持

| 元素 | 渲染效果 |
|------|---------|
| `## 标题` / `### 子标题` | 加粗标题字 |
| `**粗体**` | 加粗 |
| `- 列表项` | 圆点列表 |
| `> 引用` | 灰色文字段落 |
| `---` 分割线 | 忽略（不渲染） |
| emoji | 原样保留 |

## 工作流

1. 检查是否有 `~/.md2xhsrc` 配置文件
2. 有配置：直接运行转换
3. 无配置：需要通过参数指定 `--name` 和 `--avatar`
4. 报告生成页数和输出路径
