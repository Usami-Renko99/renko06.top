"""Regression checks for freely named uploads and deterministic builds."""
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from ensure_post_front_matter import prepare_site


class PreparePostsTests(unittest.TestCase):
    def test_history_and_legacy_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            posts = root / "_posts"
            posts.mkdir(parents=True)
            article = posts / "中文 学习.md"
            article.write_text("# 自由标题\n\n正文", encoding="utf-8")
            legacy = posts / "2026-01-02-original.md"
            original = '---\nlayout: post\ntitle: Old\ndate: 2026-01-02\ncover: /custom.jpg\n---\nOld body\n'
            legacy.write_text(original, encoding="utf-8")
            def git(*args, date="2026-01-01T20:00:00+00:00"):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                               env={**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date})
            git("init")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "first")
            first = Path(directory) / "first"
            prepare_site(root, first)
            generated = first / "_posts/2026-01-02-中文 学习.md"
            text = generated.read_text(encoding="utf-8")
            self.assertIn("2026-01-02 04:00:00 +0800", text)
            self.assertIn("title: 自由标题", text)
            self.assertIn("slug: 中文 学习", text)
            self.assertEqual((first / "_posts" / legacy.name).read_text(encoding="utf-8"), original)
            article.write_text("# 修改标题\n\n新正文", encoding="utf-8")
            git("add", ".")
            git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-m", "edit", date="2026-02-03T00:00:00+00:00")
            second = Path(directory) / "second"
            prepare_site(root, second)
            updated = (second / "_posts" / generated.name).read_text(encoding="utf-8")
            self.assertIn("2026-01-02 04:00:00 +0800", updated)
            self.assertIn("slug: 中文 学习", updated)
            self.assertEqual(article.read_text(encoding="utf-8"), "# 修改标题\n\n新正文")

    def test_collision_does_not_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            (root / "_posts").mkdir(parents=True)
            for name in ("hello.md", "2026-01-02-hello.md"):
                (root / "_posts" / name).write_text("---\ndate: 2026-01-02\n---\nHello", encoding="utf-8")
            output = Path(directory) / "build"
            with self.assertRaisesRegex(ValueError, "Conflicting"):
                prepare_site(root, output)
            self.assertFalse(output.exists())

    def test_explicit_metadata_and_invalid_date(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "repo"
            posts = root / "_posts"
            posts.mkdir(parents=True)
            article = posts / "任意名字.markdown"
            article.write_text('---\ntitle: 指定标题\ndate: 2026-03-04\npermalink: /fixed/\ncover: /image.jpg\n---\n# 正文标题\n', encoding="utf-8")
            output = Path(directory) / "build"
            prepare_site(root, output)
            text = (output / "_posts/2026-03-04-任意名字.markdown").read_text(encoding="utf-8")
            for field in ("title: 指定标题", "permalink: /fixed/", "cover: /image.jpg", "layout: post"):
                self.assertIn(field, text)
            article.write_text('---\ndate: invalid\n---\nBody', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid date"):
                prepare_site(root, Path(directory) / "invalid")


if __name__ == "__main__":
    unittest.main()
