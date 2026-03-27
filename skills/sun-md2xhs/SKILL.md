---
name: sun-md2xhs
description: 将 Markdown 文章转换为小红书长文图片卡片序列。每张图片带有用户自定义头像、蓝 V 认证标志和日期，仿照小红书原生帖子样式（白底、PingFang 字体），精确按内容高度裁切无空白。当用户说"转成小红书图片"、"生成长文卡片"、"把这篇文章转图片"、"md转小红书"、"生成小红书长文图"时触发此 skill。
---

# sun-md2xhs

将 Markdown 文章转换为小红书风格的长文图片卡片序列。

## ⚠️ 重要：使用前必须配置

**必须先通过 --init 配置用户名和头像**，才能生成图片。不支持在生成时直接传入 --name 和 --avatar。

### 第一步：询问用户信息

在调用 skill 之前，**必须先询问用户**：

> 请提供你的小红书用户名和头像图片（本地路径或网络URL），用于生成图片。

如果用户未提供头像和用户名，**不要直接生成图片**，而是回复：

> 生成小红书图片需要配置头像和用户名。请提供：
> 1. **用户名**：你在小红书上显示的名称
> 2. **头像**：本地图片路径（如 `/root/avatar.jpg`）或网络 URL

### 第二步：初始化配置

收到用户信息后，调用 --init 保存配置：

```bash
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts --init \
  --name "用户提供的用户名" \
  --avatar /path/to/avatar.jpg
```

或使用网络头像：

```bash
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts --init \
  --name "用户提供的用户名" \
  --avatar https://example.com/avatar.png
```

### 头像选项

| 头像类型 | 示例 | 说明 |
|---------|------|------|
| 本地文件 | `--avatar /path/to/avatar.jpg` | 本地图片文件路径 |
| 网络URL | `--avatar https://example.com/avatar.png` | 直接使用网络图片 |
| 默认头像 | `--avatar default` | 自动用名字首字母生成 |

### 初始化成功示例

```
✓ Config saved to ~/.md2xhsrc
  name:   SUN AI
  avatar: /path/to/avatar.jpg
```

## 生成图片

初始化完成后，只需传入 MD 文件：

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
| `--init` | 初始化模式，保存配置到 `~/.md2xhsrc` | **必须先调用** |
| `--name <name>` | 显示名称 | **与 --init 配合使用** |
| `--avatar <path>` | 头像：本地路径或 URL | **与 --init 配合使用** |
| `--out <dir>` | 输出目录 | 否，默认 `./output` |
| `--date <date>` | 日期字符串（如 `2026年03月25日`） | 否，默认今天 |
| `--width <px>` | 卡片宽度（px） | 否，默认 `1080` |
| `--chrome <path>` | 指定 Chrome/Chromium 路径 | 否，自动检测 |

## 多平台支持

脚本自动检测以下位置的 Chrome/Chromium：

| 平台 | 检测路径 |
|------|---------|
| macOS | `/Applications/Google Chrome.app/...`, Chromium, Chrome Canary |
| Linux | `/usr/bin/google-chrome`, `/usr/bin/chromium`, `/snap/bin/chromium` |
| Windows | `C:\Program Files\Google\Chrome\...\chrome.exe` |

同时会扫描 PATH 环境变量中的 `google-chrome`、`chromium`、`chrome.exe` 等命令。

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

1. 用户请求生成小红书图片
2. **检查用户是否已提供头像和用户名**，如未提供，提示用户提供
3. 调用 `--init` 保存配置到 `~/.md2xhsrc`
4. 调用脚本生成图片
5. 报告生成页数和输出路径
