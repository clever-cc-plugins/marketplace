import importlib.util
import json
import os
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "check_doc_sync", os.path.join(HERE, "..", "scripts", "check-doc-sync.py"))
cds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cds)

ORG = "clever-cc-plugins"
PROTOCOL = "# Learnings Protocol\n\n_Last updated: 2026-11-10_\n"
SKILLS = {"cc-a": ["one", "two", "three", "four", "five"], "cc-b": ["solo"], "cc-hook": []}


def footer(name):
    links = "".join('<a href="https://github.com/%s/%s">%s</a> · ' % (ORG, p, p)
                    for p in SKILLS if p != name)
    return '<p align="center">\n  %s\n</p>\n' % links


def plugin_readme(name, skills):
    rows = "".join("| `/%s:%s` | does it |\n" % (name, s) for s in skills)
    return "# %s\n\n| Skill | What |\n|---|---|\n%s\n%s" % (name, rows, footer(name))


def marketplace_readme(count=3, skip_install=None, a_skills=None):
    a_skills = SKILLS["cc-a"] if a_skills is None else a_skills
    out = ["✓ marketplace added · %d plugins available" % count]
    for n in SKILLS:
        if n != skip_install:
            out.append("$ /plugin install %s@%s" % (n, ORG))
    out.append("| [`cc-a`](https://x/cc-a) " + ", ".join("`/cc-a:%s`" % s for s in a_skills) + " |")
    out.append("| [`cc-b`](https://x/cc-b) | `/cc-b:solo` |")
    out.append("| [`cc-hook`](https://x/cc-hook) | _(hook-based)_ |")
    return "\n".join(out)


def profile_readme(plugins=3, skills=6, more=2, slash="Two"):
    return "\n".join([
        "badge/plugins-%d-F97316 badge/skills-%d-F97316" % (plugins, skills),
        "| [**cc-a**](u) | [**cc-b**](u) | [**cc-hook**](u) |",
        "- **cc-a** — `/cc-a:one` · `/cc-a:two` · `/cc-a:three` · +%d more" % more,
        "- **cc-b** — `/cc-b:solo`",
        "- **cc-hook** — runs automatically",
        "| One clear way in | %s plugins ship `/slash` commands; one runs automatically via hooks. |" % slash,
        "marketplace added · %d plugins available" % plugins,
    ])


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def build(tmp, overrides=None, protocols=None):
    overrides = overrides or {}
    for name, skills in SKILLS.items():
        base = os.path.join(tmp, name)
        for s in skills:
            os.makedirs(os.path.join(base, "plugins", name, "skills", s))
            write(os.path.join(base, "plugins", name, "skills", s, "SKILL.md"), "x")
        os.makedirs(os.path.join(base, "plugins", name, "skills", "_shared"), exist_ok=True)
        protocol = (protocols or {}).get(name, PROTOCOL)
        if skills and protocol is not None:
            write(os.path.join(base, "plugins", name, "skills", "_shared", "learnings-protocol.md"), protocol)
        write(os.path.join(base, "README.md"), overrides.get(name, plugin_readme(name, skills)))


class CheckDocSync(unittest.TestCase):
    def run_check(self, mr=None, pr=None, overrides=None, protocols=None):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp, overrides, protocols)
            mj = json.dumps({"plugins": [{"name": n} for n in SKILLS]})
            return cds.check(cds.Source(tmp), mj, mr or marketplace_readme(), pr or profile_readme())

    def test_in_sync(self):
        self.assertEqual(self.run_check(), [])

    def test_shared_dir_without_skill_md_is_not_a_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            self.assertEqual(cds.Source(tmp).skills("cc-a", "cc-a"), sorted(SKILLS["cc-a"]))

    def test_stale_plugin_count(self):
        p = self.run_check(mr=marketplace_readme(count=2))
        self.assertTrue(any("says 2 plugins available, catalog has 3" in x for x in p), p)

    def test_missing_install_line(self):
        p = self.run_check(mr=marketplace_readme(skip_install="cc-b"))
        self.assertIn("marketplace README: no install line for cc-b", p)

    def test_marketplace_row_missing_a_skill(self):
        p = self.run_check(mr=marketplace_readme(a_skills=["one", "two", "three", "four"]))
        self.assertIn("marketplace README row for cc-a: missing /five", p)

    def test_marketplace_row_lists_removed_skill(self):
        p = self.run_check(mr=marketplace_readme(a_skills=SKILLS["cc-a"] + ["gone"]))
        self.assertTrue(any("lists /gone" in x for x in p), p)

    def test_skills_badge(self):
        p = self.run_check(pr=profile_readme(skills=5))
        self.assertTrue(any("skills badge says 5, family has 6" in x for x in p), p)

    def test_plugins_badge(self):
        p = self.run_check(pr=profile_readme(plugins=4))
        self.assertTrue(any("plugins badge says 4" in x for x in p), p)

    def test_more_count(self):
        p = self.run_check(pr=profile_readme(more=1))
        self.assertTrue(any("quick-start for cc-a covers 4 skills" in x for x in p), p)

    def test_slash_word(self):
        p = self.run_check(pr=profile_readme(slash="Six"))
        self.assertTrue(any("expected 2" in x for x in p), p)

    def test_plugin_readme_missing_skill(self):
        p = self.run_check(overrides={"cc-a": plugin_readme("cc-a", SKILLS["cc-a"][:-1])})
        self.assertIn("cc-a README skill table: missing /five", p)

    def test_plugin_readme_footer_missing_link(self):
        bad = plugin_readme("cc-b", SKILLS["cc-b"]).replace("cc-hook", "other")
        p = self.run_check(overrides={"cc-b": bad})
        self.assertIn("cc-b README: footer does not link to cc-hook", p)

    def test_missing_footer_reported_once(self):
        p = self.run_check(overrides={"cc-b": "# cc-b\n\n| `/cc-b:solo` | x |\n"})
        self.assertEqual([x for x in p if x.startswith("cc-b README")], ["cc-b README: no footer found"])

    def test_missing_plugin_readme_is_a_problem_not_a_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            os.remove(os.path.join(tmp, "cc-b", "README.md"))
            mj = json.dumps({"plugins": [{"name": n} for n in SKILLS]})
            p = cds.check(cds.Source(tmp), mj, marketplace_readme(), profile_readme())
        self.assertIn("cc-b README: README.md not found", p)

    def test_missing_learnings_protocol(self):
        p = self.run_check(protocols={"cc-b": None})
        self.assertIn("cc-b: plugins/cc-b/skills/_shared/learnings-protocol.md not found", p)

    def test_learnings_protocol_differs(self):
        p = self.run_check(protocols={"cc-b": PROTOCOL + "drift\n"})
        self.assertIn("cc-b: _shared/learnings-protocol.md differs from the copy in cc-a", p)
        self.assertFalse(any(x.startswith("cc-a: _shared/learnings-protocol.md") for x in p), p)

    def test_hook_only_plugin_needs_no_learnings_protocol(self):
        self.assertFalse(any("cc-hook" in x and "learnings-protocol" in x for x in self.run_check()))

    def test_count_matches_accepts_digits_and_words_past_twelve(self):
        self.assertTrue(cds.count_matches("Seven", 7))
        self.assertTrue(cds.count_matches("14", 14))
        self.assertTrue(cds.count_matches("fourteen", 14))
        self.assertFalse(cds.count_matches("Six", 7))
        self.assertTrue(cds.count_matches("25", 25))
        self.assertFalse(cds.count_matches("twenty", 25))

    def test_missing_install_example_line(self):
        p = self.run_check(pr=profile_readme().replace("marketplace added · 3 plugins available", "x"))
        self.assertTrue(any("no '<N> plugins available' line" in x for x in p), p)

    def test_missing_slash_sentence(self):
        p = self.run_check(pr=profile_readme().replace("ship `/slash` commands", "ship commands"))
        self.assertTrue(any("no '<N> plugins ship /slash commands' sentence" in x for x in p), p)

    def test_plugin_with_documented_skills_but_none_found_is_not_hook_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            import shutil
            shutil.rmtree(os.path.join(tmp, "cc-b", "plugins"))
            mj = json.dumps({"plugins": [{"name": n} for n in SKILLS]})
            p = cds.check(cds.Source(tmp), mj, marketplace_readme(), profile_readme())
        self.assertIn("cc-b README skill table: lists /solo, which no longer exists", p)
        self.assertTrue(any("quick-start for cc-b lists skills, but none were found" in x for x in p), p)

    def test_footer_link_with_trailing_slash_or_git_suffix_counts(self):
        text = plugin_readme("cc-b", SKILLS["cc-b"]).replace('/cc-a"', '/cc-a/"').replace('/cc-hook"', '/cc-hook.git"')
        self.assertEqual(self.run_check(overrides={"cc-b": text}), [])

    def test_repo_of(self):
        git = {"name": "cc-x", "source": {"source": "git-subdir", "url": "https://github.com/o/cc-x-repo.git"}}
        self.assertEqual(cds.repo_of(git), "cc-x-repo")
        self.assertEqual(cds.repo_of({"name": "cc-y"}), "cc-y")

    def test_skills_are_read_from_the_repo_named_in_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp)
            os.rename(os.path.join(tmp, "cc-b"), os.path.join(tmp, "cc-b-repo"))
            entries = [{"name": n} for n in SKILLS]
            entries[1]["source"] = {"url": "https://github.com/%s/cc-b-repo.git" % ORG}
            p = cds.check(cds.Source(tmp), json.dumps({"plugins": entries}), marketplace_readme(), profile_readme())
        self.assertFalse(any(x.startswith("cc-b README skill table") or "README.md not found" in x for x in p), p)

    def test_main_exits_1_and_prints_drift(self):
        with mock.patch.object(cds, "check", return_value=["something drifted"]), \
                mock.patch.object(cds.Source, "read", return_value=""):
            self.assertEqual(cds.main([]), 1)


class RemoteSource(unittest.TestCase):
    def source(self, responses):
        src = cds.Source()
        src.retry_delay = 0
        src._get = lambda url: responses[url]
        return src

    def test_tree_parsing_ignores_shared_and_other_plugins(self):
        tree = {"tree": [
            {"path": "plugins/cc-x/skills/alpha/SKILL.md"},
            {"path": "plugins/cc-x/skills/alpha/notes.md"},
            {"path": "plugins/cc-x/skills/_shared/guide.md"},
            {"path": "plugins/cc-y/skills/beta/SKILL.md"},
            {"path": "plugins/cc-x/skills/gamma/SKILL.md"},
        ]}
        url = "https://api.github.com/repos/%s/cc-x/git/trees/HEAD?recursive=1" % ORG
        src = self.source({url: json.dumps(tree)})
        self.assertEqual(src.skills("cc-x", "cc-x"), ["alpha", "gamma"])

    def test_truncated_tree_fails_loudly(self):
        url = "https://api.github.com/repos/%s/cc-x/git/trees/HEAD?recursive=1" % ORG
        src = self.source({url: json.dumps({"truncated": True, "tree": []})})
        with self.assertRaises(OSError):
            src.skills("cc-x", "cc-x")

    def test_retry_once_then_succeed_and_404_is_not_retried(self):
        import urllib.error
        calls = []

        class Resp:
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"ok"

        def flaky(req, timeout=30):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.URLError("blip")
            return Resp()

        src = cds.Source()
        src.retry_delay = 0
        with mock.patch.object(cds.urllib.request, "urlopen", flaky):
            self.assertEqual(src._get("https://example.invalid/x"), "ok")
        self.assertEqual(len(calls), 2)

        def gone(req, timeout=30):
            calls.append(1)
            raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, None)
        before = len(calls)
        with mock.patch.object(cds.urllib.request, "urlopen", gone):
            with self.assertRaises(FileNotFoundError):
                src._get("https://example.invalid/y")
        self.assertEqual(len(calls) - before, 1)

    def test_main_exits_2_when_the_check_cannot_run(self):
        with mock.patch.object(cds.Source, "read", side_effect=OSError("offline")):
            self.assertEqual(cds.main([]), 2)

    def test_main_exits_2_for_missing_profile_readme_in_root_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(cds.main(["--root", tmp]), 2)


if __name__ == "__main__":
    unittest.main()
