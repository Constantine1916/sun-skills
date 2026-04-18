# sun-skills

English | [中文](./README.zh.md)

Sun 分享的 Skills，用于提高与 Claude Code 协同工作的日常效率。

## 前置要求

- 已安装 Node.js 环境
- 能够运行 `npx bun` 命令

## 安装

### 快速安装（推荐）

```bash
npx skills add sun/sun-skills
```

### 发布到 ClawHub / OpenClaw

本仓库支持将每个 `skills/sun-*` 目录作为独立的 ClawHub skill 进行发布。

```bash
# 预览将要发布的内容
./scripts/sync-clawhub.sh --dry-run

# 发布 ./skills 下所有有变化的 skill
./scripts/sync-clawhub.sh --all
```

ClawHub 以独立方式安装 skills，而非作为单一 marketplace 包。发布后，用户可以安装特定的 skill，例如：

```bash
clawhub install sun-md2xhs
clawhub install sun-report
```

发布到 ClawHub 会根据 ClawHub 的注册规则，以 `MIT-0` 许可证发布所发布的 skill。

### 注册为插件市场

在 Claude Code 中运行以下命令：

```bash
/plugin marketplace add Constantine1916/sun-skills
```

### 安装 Skills

**方式一：通过浏览 UI**

1. 选择 **Browse and install plugins**
2. 选择 **sun-skills**
3. 选择 **sun-skills** 插件
4. 选择 **Install now**

**方式二：直接安装**

```bash
# 安装市场的单一插件
/plugin install sun-skills@sun-skills
```

**方式三：告诉 Agent**

直接在 Claude Code 中说：

> 请从 github.com/Constantine1916/sun-skills 安装 Skills

### 可用插件

市场现在暴露单一插件，使每个 skill 精确注册一次。

| 插件 | 描述 | 包含内容 |
|--------|-------------|----------|
| **sun-skills** | 提高日常工作效率的 Skills | 本仓库中的所有 skills |

## 更新 Skills

要将 skills 更新到最新版本：

1. 在 Claude Code 中运行 `/plugin`
2. 切换到 **Marketplaces** 标签（使用方向键或 Tab）
3. 选择 **sun-skills**
4. 选择 **Update marketplace**

你也可以 **Enable auto-update** 以自动获取最新版本。

## 可用 Skills

### 内容生成技能

#### sun-md2xhs

将 Markdown 文章转换为小红书风格的长文图片卡片序列。每张卡片带有用户自定义头像、蓝 V 认证标志和日期，仿照小红书原生帖子样式（白底、PingFang 字体），精确按内容高度裁切无空白。

```bash
# 首次使用：保存名称和头像到 ~/.md2xhsrc
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts --init \
  --name "你的名字" \
  --avatar /path/to/avatar.jpg

# 日常使用：将 MD 文件转换为小红书图片
bun ~/.claude/skills/sun-md2xhs/scripts/md2xhs.ts ~/article.md --out ~/Desktop/xhs-output/
```

**参数说明：**

| 参数 | 说明 | 是否必填 |
|------|------|--------|
| `--init` | 初始化模式，保存配置到 `~/.md2xhsrc` | 首次使用 |
| `--name <name>` | 显示名称 | 初始化后可省略 |
| `--avatar <path>` | 头像图片路径 | 初始化后可省略 |
| `--out <dir>` | 输出目录 | 否，默认 `./output` |
| `--date <date>` | 日期字符串（如 `2026年03月25日`） | 否，默认今天 |
| `--width <px>` | 卡片宽度（px） | 否，默认 `1080` |

**Markdown 支持：**

| 元素 | 渲染效果 |
|------|---------|
| `## 标题` / `### 子标题` | 加粗标题字 |
| `**粗体**` | 加粗 |
| `- 列表项` | 圆点列表 |
| `> 引用` | 灰色文字段落 |
| `---` 分割线 | 忽略（不渲染） |
| emoji | 原样保留 |

**输出结构：**

```
<out-dir>/
  <filename>-01.png   ← 第 1 页
  <filename>-02.png   ← 第 2 页
  ...
  .tmp-html/          ← 中间 HTML 文件
```

### 汇报生成技能

#### sun-report

基于 GitHub、GitLab 或两者的账号级远端提交生成程序员日报或周报。该 skill 会将已推送的工作内容归纳为模块级输出，而不是直接罗列原始 commit。

**安装方式：**

按上面的仓库安装方式安装 `sun-skills` 后，即可使用其中包含的 `sun-report`。

**前置依赖：**

- 使用 GitHub 时需要安装 `gh`
- 使用 GitLab 时需要安装 `glab`
- 支持通过传入实例 hostname 使用自建 GitLab

**在 Claude Code / Codex 中使用：**

```text
$sun-report 帮我写一个日报
$sun-report 帮我写一个周报
```

示例提示词：

```text
$sun-report 帮我按 GitHub 提交写一个日报
$sun-report 帮我按 GitHub 提交写一个周报
$sun-report 帮我按 GitLab 提交写一个周报
```

这个 skill 会：

- 先询问你的工作提交是在 GitHub、GitLab 还是两者都有
- 在取数前检查 `gh` / `glab` 的登录状态
- 通过 hostname 支持自建 GitLab
- 只统计已经推送到远端平台的提交
- 统一按北京时间计算日报和周报时间范围

**直接运行脚本：**

```bash
python3 ~/.codex/skills/sun-report/scripts/sun_report.py \
  --report-type weekly \
  --providers github
```

```bash
python3 ~/.codex/skills/sun-report/scripts/sun_report.py \
  --report-type weekly \
  --providers gitlab \
  --gitlab-host gitlab.company.com
```

## 环境配置

部分 skills 需要 API 密钥或自定义配置。可以在 `.env` 文件中设置环境变量：

1. CLI 环境变量（例如 `OPENAI_API_KEY=xxx /sun-skill ...`）
2. `process.env`（系统环境）
3. `<cwd>/.sun-skills/.env`（项目级别）
4. `~/.sun-skills/.env`（用户级别）

## 免责声明

本项目按"原样"提供，供个人和教育使用。

## 致谢

本项目灵感来自 [baoyu-skills](https://github.com/JimLiu/baoyu-skills)。
