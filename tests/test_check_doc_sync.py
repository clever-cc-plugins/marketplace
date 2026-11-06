import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "check_doc_sync", os.path.join(HERE, "..", "scripts", "check-doc-sync.py"))
cds = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cds)

ORG = "clever-cc-plugins"
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


def build(tmp, overrides=None):
    overrides = overrides or {}
    for name, skills in SKILLS.items():
        base = os.path.join(tmp, name)
        for s in skills:
            os.makedirs(os.path.join(base, "plugins", name, "skills", s))
            write(os.path.join(base, "plugins", name, "skills", s, "SKILL.md"), "x")
        os.makedirs(os.path.join(base, "plugins", name, "skills", "_shared"), exist_ok=True)
        write(os.path.join(base, "README.md"), overrides.get(name, plugin_readme(name, skills)))


class CheckDocSync(unittest.TestCase):
    def run_check(self, mr=None, pr=None, overrides=None):
        with tempfile.TemporaryDirectory() as tmp:
            build(tmp, overrides)
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
        self.assertTrue(any("expected Two" in x for x in p), p)

    def test_plugin_readme_missing_skill(self):
        p = self.run_check(overrides={"cc-a": plugin_readme("cc-a", SKILLS["cc-a"][:-1])})
        self.assertIn("cc-a README skill table: missing /five", p)

    def test_plugin_readme_footer_missing_link(self):
        bad = plugin_readme("cc-b", SKILLS["cc-b"]).replace("cc-hook", "other")
        p = self.run_check(overrides={"cc-b": bad})
        self.assertIn("cc-b README: footer does not link to cc-hook", p)


if __name__ == "__main__":
    unittest.main()
