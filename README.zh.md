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
clawhub install sun-imagine
clawhub install sun-markdown-to-html
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

敬请期待！本仓库正在积极开发中。

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
