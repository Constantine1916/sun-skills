import importlib.util
import sys
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "skills" / "sun-report" / "scripts" / "sun_report.py"


class SunReportTests(unittest.TestCase):
    maxDiff = None

    def load_module(self):
        if not MODULE_PATH.exists():
            self.fail(f"Expected script at {MODULE_PATH}")
        spec = importlib.util.spec_from_file_location("sun_report", MODULE_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_daily_window_uses_beijing_boundaries(self):
        mod = self.load_module()
        now = datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        window = mod.build_time_window("daily", now)
        self.assertEqual(window.label, "日报")
        self.assertEqual(window.start_local.isoformat(), "2026-04-18T00:00:00+08:00")
        self.assertEqual(window.end_local.isoformat(), "2026-04-18T23:59:59.999999+08:00")

    def test_weekly_window_starts_on_monday(self):
        mod = self.load_module()
        now = datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
        window = mod.build_time_window("weekly", now)
        self.assertEqual(window.label, "周报")
        self.assertEqual(window.start_local.isoformat(), "2026-04-13T00:00:00+08:00")
        self.assertEqual(window.end_local.isoformat(), "2026-04-19T23:59:59.999999+08:00")

    def test_github_push_events_expand_to_commit_records(self):
        mod = self.load_module()
        events = [
            {
                "created_at": "2026-04-18T02:12:00Z",
                "repo": {"name": "acme/api"},
                "payload": {
                    "ref": "refs/heads/main",
                    "commits": [
                        {"sha": "abc1234", "message": "feat: add exporter"},
                    ],
                },
            }
        ]
        records = mod.normalize_github_events(events, "github.com")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["repo"], "acme/api")
        self.assertEqual(records[0]["branch"], "main")
        self.assertEqual(records[0]["title"], "feat: add exporter")
        self.assertEqual(records[0]["source_detail"], "full")

    def test_github_push_events_expand_compare_range_when_commits_are_missing(self):
        mod = self.load_module()
        events = [
            {
                "type": "PushEvent",
                "created_at": "2026-04-18T09:49:07Z",
                "repo": {"name": "Constantine1916/operation-content-platform"},
                "payload": {
                    "ref": "refs/heads/main",
                    "before": "cb6c4ababdffde9e8acb5cafbf9272b025a94dd0",
                    "head": "207a666081c07617bf983295539185e6f86a28e1",
                },
                "actor": {"login": "Constantine1916"},
            }
        ]
        compare_map = {
            (
                "Constantine1916/operation-content-platform",
                "cb6c4ababdffde9e8acb5cafbf9272b025a94dd0",
                "207a666081c07617bf983295539185e6f86a28e1",
            ): [
                {
                    "sha": "207a666081c07617bf983295539185e6f86a28e1",
                    "commit": {
                        "message": "fix: use Beijing date ranges for daily stats",
                    },
                    "html_url": "https://github.com/Constantine1916/operation-content-platform/commit/207a666081c07617bf983295539185e6f86a28e1",
                }
            ]
        }
        records = mod.normalize_github_events(events, "github.com", compare_map)
        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["title"],
            "fix: use Beijing date ranges for daily stats",
        )
        self.assertEqual(records[0]["sha"], "207a666081c07617bf983295539185e6f86a28e1")
        self.assertEqual(records[0]["repo"], "Constantine1916/operation-content-platform")
        self.assertEqual(records[0]["branch"], "main")

    def test_gitlab_summary_mode_marks_degraded_records(self):
        mod = self.load_module()
        events = [
            {
                "created_at": "2026-04-18T03:00:00Z",
                "project_id": 9,
                "project": {"path_with_namespace": "team/app"},
                "push_data": {
                    "commit_count": 3,
                    "commit_title": "Bulk update",
                    "ref": "main",
                },
            }
        ]
        records = mod.normalize_gitlab_events(events, "gitlab.example.com", {})
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["source_detail"], "summary-only")
        self.assertIn("summary-only", records[0]["notes"][0])

    def test_render_daily_report_uses_summary_layout(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "daily",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "acme/api",
                "sha": "abc1234",
                "title": "feat: add exporter",
                "message": "feat: add exporter",
                "url": "https://github.com/acme/api/commit/abc1234",
                "pushed_at_utc": "2026-04-18T02:12:00Z",
                "pushed_at_bjt": "2026-04-18 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            }
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertIn("# 日报", report)
        self.assertIn("## 时间范围", report)
        self.assertIn("今天主要推进了以下几项工作：", report)
        self.assertIn("- ", report)
        self.assertNotIn("## 关键提交", report)
        self.assertNotIn("## 原始提交清单", report)
        self.assertNotIn("## 风险与问题", report)
        self.assertNotIn("整体来看", report)

    def test_render_daily_report_uses_module_level_outputs(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "daily",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "1111111",
                "title": "fix: split mobile image preview layout",
                "message": "fix: split mobile image preview layout",
                "url": "",
                "pushed_at_utc": "2026-04-18T09:12:00Z",
                "pushed_at_bjt": "2026-04-18 17:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "2222222",
                "title": "fix: align image preview controls mobile",
                "message": "fix: align image preview controls mobile",
                "url": "",
                "pushed_at_utc": "2026-04-18T08:12:00Z",
                "pushed_at_bjt": "2026-04-18 16:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "3333333",
                "title": "docs: h5 adaptation implementation plan",
                "message": "docs: h5 adaptation implementation plan",
                "url": "",
                "pushed_at_utc": "2026-04-18T07:12:00Z",
                "pushed_at_bjt": "2026-04-18 15:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertIn("- operation-content-platform：", report)
        self.assertIn("图片预览：移动端预览布局拆分、移动端控制交互", report)
        self.assertIn("H5 适配：实现方案", report)
        self.assertNotIn("## 风险与问题", report)
        self.assertNotIn("从项目分布看", report)

    def test_summarize_title_phrase_avoids_generic_fillers_for_english_titles(self):
        mod = self.load_module()
        phrase = mod.summarize_title_phrase("docs: readme in chinese")
        self.assertIn("README", phrase)
        self.assertNotIn("相关能力", phrase)
        self.assertNotIn("相关内容", phrase)

    def test_render_weekly_report_uses_longer_summary_layout(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "weekly",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/app",
                "sha": "abc1234",
                "title": "feat: add favorites and profile center",
                "message": "feat: add favorites and profile center",
                "url": "https://github.com/team/app/commit/abc1234",
                "pushed_at_utc": "2026-04-18T02:12:00Z",
                "pushed_at_bjt": "2026-04-18 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            }
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertIn("# 周报", report)
        self.assertIn("本周工作主要集中在", report)
        self.assertIn("核心推进方向包括：", report)
        self.assertIn("从项目分布看", report)
        self.assertNotIn("## 原始提交清单", report)

    def test_collect_repo_modules_groups_weekly_work_by_function_area(self):
        mod = self.load_module()
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "1111111",
                "title": "docs: h5 adaptation design spec",
                "message": "docs: h5 adaptation design spec",
                "url": "",
                "pushed_at_utc": "2026-04-18T02:12:00Z",
                "pushed_at_bjt": "2026-04-18 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "2222222",
                "title": "docs: h5 adaptation implementation plan",
                "message": "docs: h5 adaptation implementation plan",
                "url": "",
                "pushed_at_utc": "2026-04-17T02:12:00Z",
                "pushed_at_bjt": "2026-04-17 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "3333333",
                "title": "fix: mobile viewport helpers",
                "message": "fix: mobile viewport helpers",
                "url": "",
                "pushed_at_utc": "2026-04-16T02:12:00Z",
                "pushed_at_bjt": "2026-04-16 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "4444444",
                "title": "fix: align image preview controls mobile",
                "message": "fix: align image preview controls mobile",
                "url": "",
                "pushed_at_utc": "2026-04-15T02:12:00Z",
                "pushed_at_bjt": "2026-04-15 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "5555555",
                "title": "fix: adapt image preview lightbox mobile",
                "message": "fix: adapt image preview lightbox mobile",
                "url": "",
                "pushed_at_utc": "2026-04-14T02:12:00Z",
                "pushed_at_bjt": "2026-04-14 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
        ]
        module_groups = mod.collect_repo_modules(records)
        self.assertEqual(module_groups[0][0], "team/operation-content-platform")
        self.assertIn(("H5 适配", ["设计方案", "实现方案", "viewport 辅助处理"]), module_groups[0][1])
        self.assertIn(("图片预览", ["移动端控制交互", "灯箱体验"]), module_groups[0][1])

    def test_render_weekly_report_avoids_template_like_ai_phrases(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "weekly",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "abc1234",
                "title": "feat: add favorites and profile center",
                "message": "feat: add favorites and profile center",
                "url": "https://github.com/team/operation-content-platform/commit/abc1234",
                "pushed_at_utc": "2026-04-18T02:12:00Z",
                "pushed_at_bjt": "2026-04-18 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "def5678",
                "title": "fix: favorite button interaction",
                "message": "fix: favorite button interaction",
                "url": "https://github.com/team/operation-content-platform/commit/def5678",
                "pushed_at_utc": "2026-04-17T03:30:00Z",
                "pushed_at_bjt": "2026-04-17 11:30:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "9876abc",
                "title": "docs: readme in chinese",
                "message": "docs: readme in chinese",
                "url": "https://github.com/team/vibe-studying/commit/9876abc",
                "pushed_at_utc": "2026-04-16T05:00:00Z",
                "pushed_at_bjt": "2026-04-16 13:00:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "2468ace",
                "title": "chore: scaffold frontend, backend, agent packages",
                "message": "chore: scaffold frontend, backend, agent packages",
                "url": "https://github.com/team/vibe-studying/commit/2468ace",
                "pushed_at_utc": "2026-04-15T06:20:00Z",
                "pushed_at_bjt": "2026-04-15 14:20:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "abcd246",
                "title": "fix: merge author info into image gradient overlay (design a)",
                "message": "fix: merge author info into image gradient overlay (design a)",
                "url": "https://github.com/team/vibe-studying/commit/abcd246",
                "pushed_at_utc": "2026-04-14T08:10:00Z",
                "pushed_at_bjt": "2026-04-14 16:10:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertIn("本周工作主要集中在", report)
        self.assertIn("- operation-content-platform：", report)
        self.assertIn("- vibe-studying：", report)
        self.assertIn("从项目分布看", report)
        self.assertIn("没有完全收口", report)
        self.assertIn("后续还需要继续打磨", report)
        self.assertNotIn("围绕 ", report)
        self.assertNotIn("相关能力", report)
        self.assertNotIn("相关内容", report)
        self.assertNotIn("等内容", report)

    def test_render_weekly_report_surfaces_module_level_outputs(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "weekly",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "1111111",
                "title": "docs: h5 adaptation design spec",
                "message": "docs: h5 adaptation design spec",
                "url": "",
                "pushed_at_utc": "2026-04-18T02:12:00Z",
                "pushed_at_bjt": "2026-04-18 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "2222222",
                "title": "docs: h5 adaptation implementation plan",
                "message": "docs: h5 adaptation implementation plan",
                "url": "",
                "pushed_at_utc": "2026-04-17T02:12:00Z",
                "pushed_at_bjt": "2026-04-17 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "3333333",
                "title": "fix: mobile viewport helpers",
                "message": "fix: mobile viewport helpers",
                "url": "",
                "pushed_at_utc": "2026-04-16T02:12:00Z",
                "pushed_at_bjt": "2026-04-16 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "4444444",
                "title": "fix: align image preview controls mobile",
                "message": "fix: align image preview controls mobile",
                "url": "",
                "pushed_at_utc": "2026-04-15T02:12:00Z",
                "pushed_at_bjt": "2026-04-15 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/operation-content-platform",
                "sha": "5555555",
                "title": "fix: adapt image preview lightbox mobile",
                "message": "fix: adapt image preview lightbox mobile",
                "url": "",
                "pushed_at_utc": "2026-04-14T02:12:00Z",
                "pushed_at_bjt": "2026-04-14 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "6666666",
                "title": "docs: rewrite readme reflect current project state",
                "message": "docs: rewrite readme reflect current project state",
                "url": "",
                "pushed_at_utc": "2026-04-18T03:12:00Z",
                "pushed_at_bjt": "2026-04-18 11:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "7777777",
                "title": "docs: readme in chinese",
                "message": "docs: readme in chinese",
                "url": "",
                "pushed_at_utc": "2026-04-17T03:12:00Z",
                "pushed_at_bjt": "2026-04-17 11:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "8888888",
                "title": "chore: scaffold frontend, backend, agent packages",
                "message": "chore: scaffold frontend, backend, agent packages",
                "url": "",
                "pushed_at_utc": "2026-04-16T03:12:00Z",
                "pushed_at_bjt": "2026-04-16 11:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/vibe-studying",
                "sha": "9999999",
                "title": "chore: gitignore, remove node modules from tracking",
                "message": "chore: gitignore, remove node modules from tracking",
                "url": "",
                "pushed_at_utc": "2026-04-15T03:12:00Z",
                "pushed_at_bjt": "2026-04-15 11:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            },
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertIn("H5 适配：设计方案、实现方案、viewport 辅助处理", report)
        self.assertIn("图片预览：移动端控制交互、灯箱体验", report)
        self.assertIn("README 与文档：当前项目说明更新、中文 README", report)
        self.assertIn("项目脚手架：前端、后端和 agent 包结构", report)
        self.assertIn("工程配置：.gitignore 与依赖跟踪清理", report)

    def test_render_report_shows_risks_only_when_needed(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "daily",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "gitlab",
                "host": "gitlab.example.com",
                "repo": "team/app",
                "sha": "",
                "title": "Bulk update",
                "message": "Bulk update",
                "url": "",
                "pushed_at_utc": "2026-04-18T03:00:00Z",
                "pushed_at_bjt": "2026-04-18 11:00:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "summary-only",
                "notes": ["summary-only: event payload did not expose full commit details"],
            }
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertIn("## 风险与问题", report)

    def test_render_report_does_not_infer_risk_from_commit_keywords_alone(self):
        mod = self.load_module()
        window = mod.build_time_window(
            "weekly",
            datetime(2026, 4, 18, 15, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
        )
        records = [
            {
                "provider": "github",
                "host": "github.com",
                "repo": "team/app",
                "sha": "abc1234",
                "title": "hotfix: adjust mobile viewport helper",
                "message": "hotfix: adjust mobile viewport helper",
                "url": "https://github.com/team/app/commit/abc1234",
                "pushed_at_utc": "2026-04-18T02:12:00Z",
                "pushed_at_bjt": "2026-04-18 10:12:00",
                "branch": "main",
                "author_display": "sun",
                "source_detail": "full",
                "notes": [],
            }
        ]
        report = mod.render_markdown_report(window, records, [])
        self.assertNotIn("## 风险与问题", report)

    def test_parse_provider_selection_supports_both(self):
        mod = self.load_module()
        self.assertEqual(mod.parse_providers("github,gitlab"), ["github", "gitlab"])

    def test_parse_provider_selection_rejects_unknown_provider(self):
        mod = self.load_module()
        with self.assertRaises(ValueError):
            mod.parse_providers("github,bitbucket")


if __name__ == "__main__":
    unittest.main()
