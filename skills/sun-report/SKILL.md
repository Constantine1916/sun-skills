---
name: sun-report
description: 为程序员生成日报或周报，基于 GitHub、GitLab 或两者的账号级远端提交记录输出总结型工作汇报。用户说“写日报”“写周报”“汇总今天提交”“汇总本周提交”“生成 commit 周报”“按 GitHub/GitLab 提交写汇报”时触发。必须先询问提交在哪个平台，GitLab 场景必须确认实例 hostname，自建 GitLab 也支持；只统计已经推送到远端的平台提交；所有时间窗口都使用北京时间；默认输出总结段落和无序列表，不直接展示关键提交或原始提交清单。
---

# sun-report

生成基于远端提交记录的日报或周报。

## Workflow

严格按这个顺序执行：

1. 询问用户工作提交在哪个平台：
   - `GitHub`
   - `GitLab`
   - `两者都有`
2. 如果包含 GitHub：
   - 默认 host 用 `github.com`
   - 先运行 `gh auth status --hostname <host>`
   - 未登录时要求用户运行 `gh auth login --hostname <host>`
3. 如果包含 GitLab：
   - 先询问 GitLab hostname
   - 必须运行 `glab auth status --hostname <host>`
   - 未登录时要求用户运行 `glab auth login --hostname <host>`
4. 两个平台都选时，两个都必须通过认证检查后再继续。
5. 询问生成 `日报` 还是 `周报`。
6. 使用北京时间：
   - 日报：当天 `00:00:00` 到 `23:59:59.999999`
   - 周报：本周一 `00:00:00` 到本周日 `23:59:59.999999`
7. 运行 bundled script 收集并归一化远端提交记录。
8. 输出：
   - 总结型汇报正文
   - 无序列表形式的工作内容归纳
   - 必要时的风险或数据异常说明

## Run the Script

不要手写临时 API 调用。始终运行 bundled script：

```bash
python3 <skill-dir>/scripts/sun_report.py \
  --report-type <daily|weekly> \
  --providers <github|gitlab|github,gitlab> \
  --github-host <github-host> \
  --gitlab-host <gitlab-host>
```

示例：

```bash
python3 <skill-dir>/scripts/sun_report.py \
  --report-type daily \
  --providers github
```

```bash
python3 <skill-dir>/scripts/sun_report.py \
  --report-type weekly \
  --providers gitlab \
  --gitlab-host gitlab.company.com
```

```bash
python3 <skill-dir>/scripts/sun_report.py \
  --report-type weekly \
  --providers github,gitlab \
  --gitlab-host gitlab.company.com
```

## Output Rules

- 默认输出总结型报告，不直接展示 `关键提交` 或 `原始提交清单`。
- 日报要更短：
  - 一句开场
  - 一个无序列表
- 日报也按 `功能/模块级` 归纳，但每个重点仓库尽量只保留 `1~3` 个当天实际推进的模块，保持简短。
- 不再追加重复性的总结段落
- 周报要更完整：
  - 一段总述
  - 一个无序列表
  - 一段总结
- 周报首段先点出本周主要集中在哪些项目。
- 周报列表项优先按 `功能/模块级` 归纳，不要只写抽象方向词。
- 周报列表项可用 `仓库名：模块 1：产出 A、产出 B；模块 2：产出 C、产出 D` 的形式。
- 每个重点仓库尽量体现 `2~4` 个具体模块，以及每个模块下推进了什么，不要只给一句泛化总结。
- 周报结尾要补一句整体总结，说明本周主要推进了哪些模块、哪些模块看起来还没完全收口、后续可能还需要继续打磨。
- 无序列表里的每一项都应该是对一组提交的归纳，不要直接照抄 commit message。
- 仓库名或项目名可以提，但不是必须。
- 避免明显模板味的兜底词：
  - `围绕`
  - `相关能力`
  - `相关内容`
  - `等内容`
- `风险与问题` 只在真的有问题时出现：
  - 平台取数失败
  - GitLab 只能拿到 `summary-only`
- 不要仅凭 commit 标题里出现 `hotfix`、`revert`、`failure` 之类的词就自动判定为风险

## Failure Handling

- 如果某个平台 CLI 不存在，直接告诉用户缺少 `gh` 或 `glab`。
- 如果认证失败，停止并给出准确登录命令。
- 如果一个平台成功、另一个失败：
  - 继续输出成功平台的汇报
  - 同时保留 `数据获取异常`
- 如果两个平台都失败：
  - 不要伪造日报或周报内容
  - 只输出失败原因和下一步排查建议
- 如果 GitLab 只能拿到 push 摘要：
  - 明确标记为 `summary-only`
  - 提醒总结可能不完整

## Provider Notes

遇到自建 GitLab、事件缺失、批量 push 只有摘要等情况时，查看：

- [references/provider-notes.md](references/provider-notes.md)
