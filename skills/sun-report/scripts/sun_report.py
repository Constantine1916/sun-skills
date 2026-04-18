#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote
from zoneinfo import ZoneInfo


BEIJING = ZoneInfo("Asia/Shanghai")
CONVENTIONAL_PREFIX_RE = re.compile(
    r"^(feat|fix|chore|docs|refactor|test|perf|build|ci|style)(\([^)]+\))?:\s*",
    re.IGNORECASE,
)
LEADING_VERB_RE = re.compile(
    r"^(add|fix|refine|show|use|update|improve|support|handle|enable|build|remove|adjust|simplify|complete|finish)\s+",
    re.IGNORECASE,
)
PHRASE_REPLACEMENTS = [
    ("rewrite landing page ai树洞 positioning", "重写 ai树洞 落地页定位"),
    ("gitignore、remove node modules from tracking", "整理 .gitignore，移除 node_modules 跟踪"),
    ("ai 画廊 卡片体验", "AI 画廊卡片体验"),
    ("rewrite readme reflect current project state", "重写 README，更新当前项目说明"),
    ("image upload action", "图片上传操作"),
    ("preview toolbar actions", "预览工具栏操作"),
    ("redesign image preview lightbox", "图片预览灯箱交互"),
    ("image preview lightbox", "图片预览灯箱交互"),
    ("ai gallery card ux", "AI 画廊卡片体验"),
    ("ai 画廊 card ux", "AI 画廊卡片体验"),
    ("reflect current project state", "更新当前项目说明"),
    ("readme in chinese", "中文 README"),
    ("vrm model now included in repo", "将 VRM 示例模型纳入仓库"),
    ("include sample vrm model in repo", "补充 VRM 示例模型"),
    ("scaffold frontend, backend, agent packages", "前端、后端和 agent 包结构"),
    ("merge author info into image gradient overlay (design a)", "作者信息与图片叠层样式"),
    ("merge author info into image gradient overlay", "作者信息与图片叠层样式"),
    ("rebrand to ai树洞 (aicave.cn)", "切换到 ai树洞 品牌"),
    ("favorites and profile center", "收藏功能与个人中心"),
    ("favorite button interaction", "收藏按钮交互"),
    ("profile video counts", "个人页视频数量展示"),
    ("beijing date ranges", "北京时间日期范围"),
    ("daily stats", "日统计逻辑"),
    ("preview url", "预览地址"),
    ("profile center", "个人中心"),
    ("favorite button", "收藏按钮"),
    ("video counts", "视频数量展示"),
    ("video count", "视频数量展示"),
    ("favorites", "收藏功能"),
    ("favorite", "收藏"),
    ("profile", "个人资料"),
    ("interaction", "交互"),
    ("stats", "统计"),
    ("exporter", "导出能力"),
    ("workspace", "工作区"),
    ("bootstrap", "初始化"),
    ("session", "会话"),
    ("gallery", "画廊"),
    ("readme", "README"),
    ("sample vrm model", "VRM 示例模型"),
    ("vrm model", "VRM 模型"),
    ("author info", "作者信息"),
    ("image gradient overlay", "图片叠层样式"),
    ("gradient overlay", "叠层样式"),
    ("lightbox", "灯箱"),
    ("card ux", "卡片体验"),
    ("ai gallery", "AI 画廊"),
    ("ai 画廊", "AI 画廊"),
    ("landing page", "落地页"),
    ("positioning", "定位"),
    ("remove node modules from tracking", "移除 node_modules 跟踪"),
    ("gitignore", ".gitignore"),
    ("node modules", "node_modules"),
    ("local worktree", "本地 worktree"),
    ("rewrite", "重写"),
    ("frontend", "前端"),
    ("backend", "后端"),
    ("packages", "包结构"),
    ("package", "包结构"),
    ("scaffold", "脚手架"),
    ("public", "公开"),
    ("browse", "浏览"),
    ("layout", "布局"),
    ("design a", "方案 A"),
]
WORD_REPLACEMENTS = [
    ("gitignore", ".gitignore"),
    ("node_modules", "node_modules"),
    ("image", "图片"),
    ("upload", "上传"),
    ("action", "操作"),
    ("landing", "落地"),
    ("page", "页面"),
    ("positioning", "定位"),
    ("remove", "移除"),
    ("tracking", "跟踪"),
    ("toolbar", "工具栏"),
    ("preview", "预览"),
    ("profile", "个人资料"),
    ("gallery", "画廊"),
    ("ux", "体验"),
]
SUMMARY_PATTERNS = [
    (("beijing", "date"), "时间范围与统计逻辑"),
    (("daily", "stat"), "时间范围与统计逻辑"),
    (("favorite", "profile"), "收藏与个人中心能力"),
    (("favorite", "button"), "收藏交互与按钮体验"),
    (("video", "count"), "视频展示与统计能力"),
    (("public", "profile"), "公开个人资料与浏览能力"),
    (("site", "logo"), "页面展示与品牌元素"),
    (("hotspot", "button"), "交互入口与按钮布局"),
    (("preview", "sandbox"), "sandbox 预览链路"),
    (("proxy", "cors"), "代理与跨域链路"),
    (("workspace", "session"), "工作区与会话链路"),
    (("workspace", "bootstrap"), "工作区初始化链路"),
    (("cloudhost", "template"), "cloudhost 初始化与模板能力"),
]
MODULE_DETAIL_PATTERNS = [
    (("h5", "adaptation", "design"), "H5 适配", "设计方案"),
    (("h5", "adaptation", "implementation"), "H5 适配", "实现方案"),
    (("mobile", "viewport"), "H5 适配", "viewport 辅助处理"),
    (("split", "mobile", "image", "preview", "layout"), "图片预览", "移动端预览布局拆分"),
    (("restore", "image", "preview", "lightbox", "baseline"), "图片预览", "灯箱交互基线恢复"),
    (("image", "preview", "controls", "mobile"), "图片预览", "移动端控制交互"),
    (("image", "preview", "lightbox", "mobile"), "图片预览", "灯箱体验"),
    (("preview", "card", "touch"), "图片预览", "卡片与预览触控交互"),
    (("app", "shell", "mobile", "navigation"), "移动端页面适配", "App Shell 导航"),
    (("public", "auth", "pages", "mobile"), "移动端页面适配", "公开页与认证页"),
    (("content", "feeds", "mobile"), "移动端页面适配", "内容流"),
    (("image", "upload", "workspace"), "图片上传", "工作区上传流程"),
    (("readme", "current", "project", "state"), "README 与文档", "当前项目说明更新"),
    (("readme", "chinese"), "README 与文档", "中文 README"),
    (("scaffold", "frontend", "backend", "agent"), "项目脚手架", "前端、后端和 agent 包结构"),
    (("agent", "scripts"), "项目脚手架", "agent 脚本"),
    (("strict", "mode", "tsconfig"), "项目脚手架", "前端 TSConfig 严格模式"),
    (("agent", "runner", "dockerfile"), "项目脚手架", "agent runner 与 Dockerfile"),
    (("gitignore", "node", "modules", "tracking"), "工程配置", ".gitignore 与依赖跟踪清理"),
    (("ignore", "local", "worktrees"), "工程配置", "本地 worktree 忽略规则"),
    (("gitignore", "entries"), "工程配置", ".gitignore 清理"),
    (("superpowers", "tooling", "repo"), "工程配置", "superpowers tooling 清理"),
    (("vrm", "model"), "示例资源", "VRM 示例模型"),
    (("usevrm", "auto", "blink"), "VRM 交互", "自动眨眼与说话动画"),
    (("vrmviewer", "scene"), "VRM 交互", "Viewer 组件与 Three.js 场景"),
    (("app.vue", "vrm", "chat", "panel"), "VRM 交互", "Viewer 与聊天面板接线"),
    (("rebrand", "ai树洞"), "品牌与落地页", "品牌切换"),
    (("landing", "page", "positioning"), "品牌与落地页", "落地页定位更新"),
    (("enlarge", "landing", "page", "community", "qr"), "品牌与落地页", "社区二维码展示"),
    (("community", "qr", "landing", "page"), "品牌与落地页", "社区二维码展示"),
    (("round", "pill", "buttons", "landing"), "品牌与落地页", "统一圆角按钮样式"),
    (("editorial", "hero", "type"), "品牌与落地页", "落地页视觉改版"),
    (("gallery", "card", "ux"), "画廊展示", "卡片体验"),
    (("author", "info", "gradient", "overlay"), "画廊展示", "作者信息展示样式"),
    (("favorite", "profile"), "个人资料与收藏", "收藏与个人中心"),
    (("favorite", "button"), "个人资料与收藏", "收藏按钮交互"),
    (("public", "profile"), "个人资料与收藏", "公开个人资料与浏览"),
    (("video", "count"), "个人资料与收藏", "个人页视频数量展示"),
]
MODULE_PATTERNS = [
    (("h5", "adaptation"), "H5 适配"),
    (("viewport",), "H5 适配"),
    (("preview",), "图片预览"),
    (("lightbox",), "图片预览"),
    (("mobile",), "移动端页面适配"),
    (("readme",), "README 与文档"),
    (("frontend",), "项目脚手架"),
    (("backend",), "项目脚手架"),
    (("agent",), "项目脚手架"),
    (("scaffold",), "项目脚手架"),
    (("gitignore",), "工程配置"),
    (("node", "modules"), "工程配置"),
    (("worktree",), "工程配置"),
    (("vrm",), "示例资源"),
    (("chat", "panel"), "VRM 交互"),
    (("rebrand",), "品牌与落地页"),
    (("landing",), "品牌与落地页"),
    (("positioning",), "品牌与落地页"),
    (("gallery",), "画廊展示"),
    (("overlay",), "画廊展示"),
    (("favorite",), "个人资料与收藏"),
    (("profile",), "个人资料与收藏"),
    (("browse",), "个人资料与收藏"),
]
ONGOING_MODULES = {"H5 适配", "图片预览", "画廊展示", "个人资料与收藏", "移动端页面适配", "图片上传"}
ACTION_PREFIXES = ("完成", "补充", "补上", "完善", "优化", "处理", "修复", "推进", "梳理", "搭起", "整理")
@dataclass(frozen=True)
class TimeWindow:
    kind: str
    label: str
    start_local: datetime
    end_local: datetime

    @property
    def start_utc(self) -> datetime:
        return self.start_local.astimezone(timezone.utc)

    @property
    def end_utc(self) -> datetime:
        return self.end_local.astimezone(timezone.utc)


def normalize_host(raw: str) -> str:
    host = raw.strip()
    host = host.removeprefix("https://").removeprefix("http://")
    return host.rstrip("/")


def parse_providers(raw: str) -> list[str]:
    providers = [item.strip().lower() for item in raw.split(",") if item.strip()]
    allowed = {"github", "gitlab"}
    invalid = [item for item in providers if item not in allowed]
    if not providers or invalid:
        bad = ", ".join(invalid or ["<empty>"])
        raise ValueError(f"Unsupported providers: {bad}")
    seen = set()
    ordered = []
    for provider in providers:
        if provider in seen:
            continue
        seen.add(provider)
        ordered.append(provider)
    return ordered


def build_time_window(kind: str, now: datetime | None = None) -> TimeWindow:
    current = (now or datetime.now(BEIJING)).astimezone(BEIJING)
    day_start = current.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start.replace(hour=23, minute=59, second=59, microsecond=999999)
    if kind == "daily":
        return TimeWindow("daily", "日报", day_start, day_end)
    if kind != "weekly":
        raise ValueError(f"Unsupported report type: {kind}")
    week_start = day_start - timedelta(days=day_start.weekday())
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    return TimeWindow("weekly", "周报", week_start, week_end)


def parse_iso8601(timestamp: str) -> datetime:
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def to_beijing_display(timestamp: str) -> str:
    return parse_iso8601(timestamp).astimezone(BEIJING).strftime("%Y-%m-%d %H:%M:%S")


def in_window(timestamp: str, window: TimeWindow) -> bool:
    current = parse_iso8601(timestamp).astimezone(timezone.utc)
    return window.start_utc <= current <= window.end_utc


def dedupe_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    deduped: list[dict[str, Any]] = []
    for record in sorted(records, key=lambda item: item["pushed_at_utc"]):
        key = (
            record["provider"],
            record["host"],
            record["repo"],
            record.get("sha") or "",
            record["title"],
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def github_commit_record(
    host: str,
    repo: str,
    branch: str,
    created_at: str,
    commit: dict[str, Any],
    actor_login: str,
) -> dict[str, Any]:
    commit_body = commit.get("commit", {})
    message = commit_body.get("message") or commit.get("message") or "GitHub push"
    sha = commit.get("sha") or commit.get("id") or ""
    return {
        "provider": "github",
        "host": host,
        "repo": repo,
        "sha": sha,
        "title": message.splitlines()[0],
        "message": message,
        "url": commit.get("html_url") or (f"https://{host}/{repo}/commit/{sha}" if sha else ""),
        "pushed_at_utc": created_at,
        "pushed_at_bjt": to_beijing_display(created_at),
        "branch": branch,
        "author_display": actor_login,
        "source_detail": "full",
        "notes": [],
    }


def normalize_github_events(
    events: list[dict[str, Any]],
    host: str,
    compare_map: dict[tuple[str, str, str], list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    compare_map = compare_map or {}
    records: list[dict[str, Any]] = []
    for event in events:
        if event.get("type") not in (None, "PushEvent"):
            continue
        repo = event.get("repo", {}).get("name") or "unknown/unknown"
        payload = event.get("payload", {})
        branch = (payload.get("ref") or "").replace("refs/heads/", "") or "unknown"
        created_at = event.get("created_at")
        if not created_at:
            continue
        actor_login = event.get("actor", {}).get("login", "")
        commits = payload.get("commits", [])
        if commits:
            for commit in commits:
                records.append(
                    github_commit_record(host, repo, branch, created_at, commit, actor_login)
                )
            continue
        before = payload.get("before") or ""
        head = payload.get("head") or ""
        compare_commits = compare_map.get((repo, before, head), [])
        if compare_commits:
            records.extend(
                [
                    github_commit_record(host, repo, branch, created_at, commit, actor_login)
                    for commit in compare_commits
                ]
            )
            continue
        summary_title = f"Push to {branch}"
        records.append(
            {
                "provider": "github",
                "host": host,
                "repo": repo,
                "sha": head,
                "title": summary_title,
                "message": summary_title,
                "url": f"https://{host}/{repo}/commit/{head}" if head else "",
                "pushed_at_utc": created_at,
                "pushed_at_bjt": to_beijing_display(created_at),
                "branch": branch,
                "author_display": actor_login,
                "source_detail": "summary-only",
                "notes": ["summary-only: push event did not expose commit messages"],
            }
        )
    return dedupe_records(records)


def normalize_gitlab_events(
    events: list[dict[str, Any]],
    host: str,
    detail_map: dict[tuple[int | str, str], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for event in events:
        project_id = event.get("project_id", "unknown")
        project = event.get("project", {}).get("path_with_namespace") or str(project_id)
        push_data = event.get("push_data", {})
        created_at = event.get("created_at")
        if not created_at:
            continue
        commit_to = push_data.get("commit_to") or ""
        detail_records = detail_map.get((project_id, commit_to), [])
        if detail_records:
            records.extend(detail_records)
            continue
        title = push_data.get("commit_title") or "GitLab push"
        records.append(
            {
                "provider": "gitlab",
                "host": host,
                "repo": project,
                "sha": commit_to,
                "title": title.splitlines()[0],
                "message": title,
                "url": "",
                "pushed_at_utc": created_at,
                "pushed_at_bjt": to_beijing_display(created_at),
                "branch": push_data.get("ref") or "unknown",
                "author_display": event.get("author_username", ""),
                "source_detail": "summary-only",
                "notes": ["summary-only: event payload did not expose full commit details"],
            }
        )
    return dedupe_records(records)


def format_repo_name(repo: str) -> str:
    return repo.split("/")[-1] if "/" in repo else repo


def normalize_phrase_text(text: str) -> str:
    lowered = text.lower()
    for source, target in PHRASE_REPLACEMENTS:
        lowered = lowered.replace(source, target)
    for source, target in WORD_REPLACEMENTS:
        lowered = re.sub(rf"\b{re.escape(source)}\b", target, lowered)
    lowered = lowered.replace("_", " ").replace("-", " ")
    lowered = lowered.replace(", ", "、")
    lowered = lowered.replace(" and ", " 与 ")
    lowered = lowered.replace(" into ", " 到 ")
    lowered = lowered.replace(" in ", " ")
    lowered = lowered.replace(" for ", " ")
    lowered = lowered.replace(" to ", " ")
    lowered = re.sub(r"\s+", " ", lowered).strip()
    lowered = lowered.replace(" 相关", "相关")
    lowered = lowered.strip(" ,.;:()")
    return lowered or "工作内容整理"


def summarize_title_phrase(title: str) -> str:
    cleaned = CONVENTIONAL_PREFIX_RE.sub("", title).strip()
    cleaned = LEADING_VERB_RE.sub("", cleaned).strip()
    lowered = cleaned.lower()
    matched_summaries = [
        label for keywords, label in SUMMARY_PATTERNS if all(keyword in lowered for keyword in keywords)
    ]
    if matched_summaries:
        return matched_summaries[0]
    lowered = normalize_phrase_text(cleaned)
    if lowered.endswith(("功能", "交互", "逻辑", "能力", "展示", "支持", "范围", "体验", "流程", "文档", "布局", "样式", "结构", "模型", "品牌", "README")):
        return lowered
    return lowered


def match_keywords(text: str, keywords: tuple[str, ...]) -> bool:
    return all(keyword in text for keyword in keywords)


def derive_module_detail(title: str) -> tuple[str, str]:
    cleaned = CONVENTIONAL_PREFIX_RE.sub("", title).strip()
    lowered = cleaned.lower()
    for keywords, module, detail in MODULE_DETAIL_PATTERNS:
        if match_keywords(lowered, keywords):
            return module, detail
    for keywords, module in MODULE_PATTERNS:
        if match_keywords(lowered, keywords):
            return module, summarize_title_phrase(title)
    return "其他事项", summarize_title_phrase(title)


def group_records_by_repo(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in sorted(records, key=lambda item: item["pushed_at_utc"], reverse=True):
        grouped.setdefault(record["repo"], []).append(record)
    return grouped


def unique_ordered(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def join_phrases(phrases: list[str]) -> str:
    if not phrases:
        return "工作内容"
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]}和{phrases[1]}"
    return "、".join(phrases[:-1]) + f"以及{phrases[-1]}"


def join_detail_items(items: list[str]) -> str:
    if not items:
        return "工作内容"
    return "、".join(items)


def join_clauses(clauses: list[str]) -> str:
    if not clauses:
        return "暂无可归纳的工作"
    if len(clauses) == 1:
        return clauses[0]
    if len(clauses) == 2:
        return f"{clauses[0]}，{clauses[1]}"
    return "；".join(clauses)


def phrase_action(phrase: str) -> str:
    lowered = phrase.lower()
    if phrase.startswith("切换到"):
        return "完成"
    if phrase.startswith(("重写", "将")):
        return "补充"
    if phrase.startswith(ACTION_PREFIXES):
        return ""
    if any(token in phrase for token in ("README", "文档", "说明", "示例")):
        return "补充"
    if any(token in phrase for token in ("脚手架", "包结构")):
        return "搭起"
    if any(token in phrase for token in ("时间范围", "统计逻辑")):
        return "梳理"
    if any(token in phrase for token in ("交互", "布局", "样式", "展示", "体验", "预览")):
        return "优化"
    if any(token in phrase for token in ("跨域", "预检", "稳定")) or any(
        token in lowered for token in ("fix", "bug", "hotfix", "failure")
    ):
        return "处理"
    if any(token in phrase for token in ("链路", "流程", "工作区", "会话", "初始化")):
        return "推进"
    if any(token in phrase for token in ("品牌",)):
        return "完成"
    if any(token in phrase for token in ("能力", "功能", "支持")):
        return "补上"
    return "推进"


def compact_phrase_key(phrase: str) -> str:
    compacted = re.sub(r"[、，,；;:：()（）\s]", "", phrase)
    compacted = re.sub(r"^(完成|补充|补上|完善|优化|处理|修复|推进|梳理|搭起|整理|将|重写|切换到)", "", compacted)
    return compacted


def prune_redundant_phrases(phrases: list[str]) -> list[str]:
    pruned: list[str] = []
    keys: list[str] = []
    for phrase in phrases:
        key = compact_phrase_key(phrase)
        if not key:
            continue
        replaced = False
        for index, existing_key in enumerate(keys):
            if key in existing_key:
                replaced = True
                break
            if existing_key in key:
                pruned[index] = phrase
                keys[index] = key
                replaced = True
                break
        if not replaced:
            pruned.append(phrase)
            keys.append(key)
    return pruned


def build_repo_clauses(phrases: list[str]) -> list[str]:
    clauses: list[str] = []
    grouped: list[tuple[str, list[str]]] = []
    for phrase in phrases:
        if phrase.startswith(("将", "重写", "切换到")):
            clauses.append(phrase)
            continue
        action = phrase_action(phrase)
        if not action:
            clauses.append(phrase)
            continue
        if grouped and grouped[-1][0] == action:
            grouped[-1][1].append(phrase)
            continue
        grouped.append((action, [phrase]))
    for action, grouped_phrases in grouped:
        clauses.append(f"{action}{join_phrases(grouped_phrases)}")
    return clauses


def collect_period_phrases(records: list[dict[str, Any]]) -> list[str]:
    return prune_redundant_phrases(
        unique_ordered(
            [summarize_title_phrase(record["title"]) for record in records if record.get("title")]
        )
    )


def collect_repo_focus(records: list[dict[str, Any]]) -> list[tuple[str, list[str]]]:
    focus = []
    for repo, repo_records in group_records_by_repo(records).items():
        phrases = prune_redundant_phrases(
            unique_ordered(
                [summarize_title_phrase(record["title"]) for record in repo_records if record.get("title")]
            )
        )
        if phrases:
            focus.append((repo, phrases))
    return focus


def collect_repo_modules(records: list[dict[str, Any]]) -> list[tuple[str, list[tuple[str, list[str]]]]]:
    repo_modules: list[tuple[str, list[tuple[str, list[str]]]]] = []
    for repo, repo_records in group_records_by_repo(records).items():
        modules: dict[str, list[str]] = {}
        for record in repo_records:
            title = record.get("title")
            if not title:
                continue
            module, detail = derive_module_detail(title)
            modules.setdefault(module, []).append(detail)
        grouped = []
        for module, details in modules.items():
            grouped.append((module, prune_redundant_phrases(unique_ordered(details))))
        if grouped:
            repo_modules.append((repo, grouped))
    return repo_modules


def collect_period_modules(records: list[dict[str, Any]]) -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = {}
    for record in sorted(records, key=lambda item: item["pushed_at_utc"], reverse=True):
        title = record.get("title")
        if not title:
            continue
        module, detail = derive_module_detail(title)
        grouped.setdefault(module, []).append(detail)
    return [
        (module, prune_redundant_phrases(unique_ordered(details)))
        for module, details in grouped.items()
        if details
    ]


def build_phrase_summary_bullets(records: list[dict[str, Any]], report_kind: str) -> list[str]:
    repo_focus = collect_repo_focus(records)
    if not repo_focus:
        return ["- 本周期未检索到可见提交记录，需要人工补充工作内容。"]
    bullets = []
    for repo, phrases in repo_focus:
        repo_name = format_repo_name(repo)
        selected = phrases[:4] if report_kind == "weekly" else phrases[:3]
        clauses = build_repo_clauses(selected)
        bullets.append(f"- {repo_name}：{join_clauses(clauses)}。")
    return bullets


def build_module_summary_bullets(records: list[dict[str, Any]], report_kind: str) -> list[str]:
    repo_modules = collect_repo_modules(records)
    if not repo_modules:
        return ["- 本周期未检索到可见提交记录，需要人工补充工作内容。"]
    bullets = []
    module_limit = 4 if report_kind == "weekly" else 3
    default_detail_limit = 3 if report_kind == "weekly" else 2
    for repo, modules in repo_modules:
        repo_name = format_repo_name(repo)
        visible_modules = modules
        if any(module != "其他事项" for module, _ in modules):
            visible_modules = [(module, details) for module, details in modules if module != "其他事项"]
        module_clauses = []
        for module, details in visible_modules[:module_limit]:
            if not details:
                continue
            detail_limit = 2 if module == "工程配置" else default_detail_limit
            module_clauses.append(f"{module}：{join_detail_items(details[:detail_limit])}")
        if module_clauses:
            bullets.append(f"- {repo_name}：{join_clauses(module_clauses)}。")
    return bullets


def build_summary_bullets(records: list[dict[str, Any]], report_kind: str) -> list[str]:
    if report_kind in {"daily", "weekly"}:
        return build_module_summary_bullets(records, report_kind)
    return build_phrase_summary_bullets(records, report_kind)


def build_opening_paragraph(window: TimeWindow, records: list[dict[str, Any]]) -> str:
    if not records:
        return "本周期暂未检索到可见提交记录。"
    repo_names = unique_ordered([format_repo_name(record["repo"]) for record in records])
    repo_excerpt = "、".join(repo_names[:4])
    if window.kind == "weekly":
        return f"本周工作主要集中在{repo_excerpt}，核心推进方向包括："
    return "今天主要推进了以下几项工作："


def build_closing_paragraph(window: TimeWindow, records: list[dict[str, Any]]) -> str:
    if not records:
        if window.kind == "weekly":
            return "从提交记录看，本周暂无可见远端提交，建议结合实际工作补充总结。"
        return ""
    if window.kind == "weekly":
        period_modules = collect_period_modules(records)
        if not period_modules:
            return "从项目分布看，本周暂无足够的提交明细，建议结合实际工作补充总结。"
        completed_modules = [
            module for module, _ in period_modules if module not in ONGOING_MODULES and module != "其他事项"
        ]
        if any(module not in {"工程配置", "其他事项"} for module in completed_modules):
            completed_modules = [module for module in completed_modules if module != "工程配置"]
        ongoing_modules = [
            module for module, _ in period_modules if module in ONGOING_MODULES
        ]
        completed_details = [
            detail
            for module, details in period_modules
            if module not in ONGOING_MODULES and module != "其他事项"
            for detail in details
        ]
        if any(module not in {"工程配置", "其他事项"} for module, _ in period_modules):
            completed_details = [
                detail
                for module, details in period_modules
                if module not in ONGOING_MODULES and module not in {"工程配置", "其他事项"}
                for detail in details
            ]
        if not completed_modules:
            completed_modules = [module for module, _ in period_modules if module != "其他事项"] or ["本周重点模块"]
        completed_excerpt = join_phrases(completed_modules[:3])
        detail_excerpt = join_detail_items(unique_ordered(completed_details)[:3]) if completed_details else ""
        if ongoing_modules:
            ongoing_excerpt = join_phrases(ongoing_modules[:2])
            if detail_excerpt:
                return (
                    f"从项目分布看，这周主要把{completed_excerpt}往前推了一步，"
                    f"比较具体的产出集中在{detail_excerpt}这些点上。"
                    f"{ongoing_excerpt}这几块还在连续调整，部分衔接和细节没有完全收口，后续还需要继续打磨。"
                )
            return (
                f"从项目分布看，这周主要把{completed_excerpt}往前推了一步。"
                f"{ongoing_excerpt}这几块还在连续调整，部分衔接和细节没有完全收口，后续还需要继续打磨。"
            )
        if detail_excerpt:
            return (
                f"从项目分布看，这周主要把{completed_excerpt}往前推了一步，"
                f"比较具体的产出集中在{detail_excerpt}这些点上。"
            )
        return f"从项目分布看，这周主要把{completed_excerpt}往前推了一步。"
    return ""


def collect_risk_lines(records: list[dict[str, Any]]) -> list[str]:
    lines = []
    if any(record["source_detail"] == "summary-only" for record in records):
        lines.append("- 部分平台仅返回摘要级 push 信息，个别工作项的提交明细可能不完整。")
    return lines


def render_markdown_report(
    window: TimeWindow,
    records: list[dict[str, Any]],
    errors: list[str],
) -> str:
    opening_paragraph = build_opening_paragraph(window, records)
    summary_bullets = build_summary_bullets(records, window.kind)
    closing_paragraph = build_closing_paragraph(window, records)
    risk_lines = collect_risk_lines(records)
    sections = [
        f"# {window.label}",
        "",
        "## 时间范围",
        f"- 北京时间：{window.start_local.strftime('%Y-%m-%d %H:%M:%S')} ~ {window.end_local.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        opening_paragraph,
        "",
        *summary_bullets,
    ]
    if closing_paragraph:
        sections.extend(["", closing_paragraph])
    if risk_lines:
        sections.extend(["", "## 风险与问题", *risk_lines])
    if errors:
        sections.extend(["", "## 数据获取异常", *[f"- {item}" for item in errors]])
    sections.append("")
    return "\n".join(sections)


def ensure_command(name: str) -> None:
    if shutil.which(name):
        return
    raise RuntimeError(f"Missing required command: {name}")


def run_command(cmd: list[str]) -> str:
    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        raise RuntimeError(stderr or f"Command failed: {' '.join(cmd)}")
    return completed.stdout


def run_json_command(cmd: list[str]) -> Any:
    output = run_command(cmd).strip()
    if not output:
        return []
    decoder = json.JSONDecoder()
    docs = []
    index = 0
    while index < len(output):
        while index < len(output) and output[index].isspace():
            index += 1
        if index >= len(output):
            break
        value, next_index = decoder.raw_decode(output, index)
        docs.append(value)
        index = next_index
    if len(docs) == 1:
        return docs[0]
    return docs


def flatten_json_pages(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        flattened: list[dict[str, Any]] = []
        for item in payload:
            if isinstance(item, list):
                flattened.extend(flatten_json_pages(item))
            elif isinstance(item, dict):
                flattened.append(item)
        return flattened
    if isinstance(payload, dict):
        return [payload]
    return []


def require_gh_auth(host: str) -> None:
    run_command(["gh", "auth", "status", "--hostname", host])


def require_glab_auth(host: str) -> None:
    run_command(["glab", "auth", "status", "--hostname", host])


def github_api(host: str, path: str) -> Any:
    return run_json_command(["gh", "api", "--hostname", host, path])


def glab_api(host: str, path: str, paginate: bool = False) -> Any:
    cmd = ["glab", "api", path, "--hostname", host]
    if paginate:
        cmd.append("--paginate")
    return run_json_command(cmd)


def fetch_github_records(host: str, window: TimeWindow) -> list[dict[str, Any]]:
    user = github_api(host, "/user")
    login = user.get("login")
    if not login:
        raise RuntimeError("Unable to resolve GitHub login from gh auth session")
    payload = run_json_command(
        ["gh", "api", "--hostname", host, f"/users/{login}/events?per_page=100", "--paginate"]
    )
    events = [
        event
        for event in flatten_json_pages(payload)
        if event.get("type") == "PushEvent" and event.get("created_at") and in_window(event["created_at"], window)
    ]
    compare_map: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for event in events:
        repo = event.get("repo", {}).get("name") or ""
        payload = event.get("payload", {})
        created_at = event.get("created_at")
        actor_login = event.get("actor", {}).get("login", "")
        branch = (payload.get("ref") or "").replace("refs/heads/", "") or "unknown"
        before = payload.get("before") or ""
        head = payload.get("head") or ""
        if not repo or not created_at or not head or payload.get("commits"):
            continue
        commits: list[dict[str, Any]] = []
        try:
            if before and set(before) != {"0"}:
                compare = github_api(host, f"/repos/{repo}/compare/{before}...{head}")
                commits = compare.get("commits", [])
            else:
                commit = github_api(host, f"/repos/{repo}/commits/{head}")
                commits = [commit]
        except RuntimeError:
            commits = []
        if commits:
            compare_map[(repo, before, head)] = commits
    return normalize_github_events(events, host, compare_map)


def gitlab_commit_record(
    host: str,
    project: str,
    branch: str,
    created_at: str,
    commit: dict[str, Any],
) -> dict[str, Any]:
    sha = commit.get("id") or commit.get("short_id") or ""
    title = commit.get("title") or commit.get("message") or "GitLab commit"
    return {
        "provider": "gitlab",
        "host": host,
        "repo": project,
        "sha": sha,
        "title": title.splitlines()[0],
        "message": commit.get("message") or title,
        "url": commit.get("web_url") or "",
        "pushed_at_utc": created_at,
        "pushed_at_bjt": to_beijing_display(created_at),
        "branch": branch,
        "author_display": commit.get("author_name") or "",
        "source_detail": "full",
        "notes": [],
    }


def gitlab_project_path(host: str, project_id: int | str, cache: dict[int | str, str]) -> str:
    if project_id in cache:
        return cache[project_id]
    project = glab_api(host, f"/projects/{project_id}")
    path = project.get("path_with_namespace") or str(project_id)
    cache[project_id] = path
    return path


def expand_gitlab_event(
    host: str,
    event: dict[str, Any],
    project_cache: dict[int | str, str],
) -> list[dict[str, Any]]:
    project_id = event.get("project_id", "unknown")
    project = event.get("project", {}).get("path_with_namespace") or gitlab_project_path(host, project_id, project_cache)
    push_data = event.get("push_data", {})
    created_at = event.get("created_at")
    if not created_at:
        return []
    branch = push_data.get("ref") or "unknown"
    commit_to = push_data.get("commit_to") or ""
    commit_from = push_data.get("commit_from") or ""
    commit_count = int(push_data.get("commit_count") or 0)
    if commit_count == 1 and commit_to:
        detail = glab_api(host, f"/projects/{project_id}/repository/commits/{commit_to}")
        return [gitlab_commit_record(host, project, branch, created_at, detail)]
    if commit_count > 1 and commit_to and commit_from and set(commit_from) != {"0"}:
        compare = glab_api(
            host,
            f"/projects/{project_id}/repository/compare?from={quote(commit_from)}&to={quote(commit_to)}",
        )
        commits = compare.get("commits", [])
        if commits:
            return [
                gitlab_commit_record(host, project, branch, created_at, commit)
                for commit in commits
            ]
    return []


def fetch_gitlab_records(host: str, window: TimeWindow) -> list[dict[str, Any]]:
    user = glab_api(host, "/user")
    user_id = user.get("id")
    if not user_id:
        raise RuntimeError("Unable to resolve GitLab user from glab auth session")
    after = quote(window.start_utc.isoformat().replace("+00:00", "Z"))
    before = quote(window.end_utc.isoformat().replace("+00:00", "Z"))
    payload = glab_api(
        host,
        f"/users/{user_id}/events?action=pushed&after={after}&before={before}",
        paginate=True,
    )
    events = flatten_json_pages(payload)
    project_cache: dict[int | str, str] = {}
    detail_map: dict[tuple[int | str, str], list[dict[str, Any]]] = {}
    for event in events:
        push_data = event.get("push_data", {})
        commit_to = push_data.get("commit_to") or ""
        if not commit_to:
            continue
        try:
            details = expand_gitlab_event(host, event, project_cache)
        except RuntimeError:
            details = []
        if details:
            detail_map[(event.get("project_id", "unknown"), commit_to)] = details
    filtered_events = [
        event
        for event in events
        if event.get("created_at") and in_window(event["created_at"], window)
    ]
    return normalize_gitlab_events(filtered_events, host, detail_map)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate GitHub/GitLab daily or weekly reports")
    parser.add_argument("--report-type", choices=("daily", "weekly"), required=True)
    parser.add_argument("--providers", required=True, help="Comma-separated providers: github,gitlab")
    parser.add_argument("--github-host", default="github.com")
    parser.add_argument("--gitlab-host", default="")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--now", default="")
    return parser


def resolve_now(raw: str) -> datetime | None:
    if not raw:
        return None
    return parse_iso8601(raw)


def render_json_report(window: TimeWindow, records: list[dict[str, Any]], errors: list[str]) -> str:
    payload = {
        "label": window.label,
        "kind": window.kind,
        "start_local": window.start_local.isoformat(),
        "end_local": window.end_local.isoformat(),
        "records": records,
        "errors": errors,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    providers = parse_providers(args.providers)
    window = build_time_window(args.report_type, resolve_now(args.now))
    records: list[dict[str, Any]] = []
    errors: list[str] = []

    if "github" in providers:
        github_host = normalize_host(args.github_host)
        ensure_command("gh")
        require_gh_auth(github_host)
        try:
            records.extend(fetch_github_records(github_host, window))
        except RuntimeError as exc:
            errors.append(f"GitHub({github_host}): {exc}")

    if "gitlab" in providers:
        if not args.gitlab_host:
            raise RuntimeError("GitLab host is required when GitLab is selected")
        gitlab_host = normalize_host(args.gitlab_host)
        ensure_command("glab")
        require_glab_auth(gitlab_host)
        try:
            records.extend(fetch_gitlab_records(gitlab_host, window))
        except RuntimeError as exc:
            errors.append(f"GitLab({gitlab_host}): {exc}")

    records = dedupe_records(records)
    if args.format == "json":
        print(render_json_report(window, records, errors))
    else:
        print(render_markdown_report(window, records, errors))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
