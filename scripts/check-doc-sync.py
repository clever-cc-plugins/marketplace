#!/usr/bin/env python3
"""Check that plugin and skill documentation across the plugin family agrees.

Source of truth: each plugin repo's plugins/<name>/skills/<skill>/SKILL.md on
its default branch, plus the plugin list in .claude-plugin/marketplace.json.

Checked against that truth:
  - marketplace README: plugin count, one install line per plugin, skills per row
  - org profile README (.github): plugin and skill badges, "+N more" counts,
    "<N> plugins ship /slash commands", plugin table, install-example count
  - every plugin README: skill table rows, footer links to the other plugins

Usage:
  python3 scripts/check-doc-sync.py                 # fetch from GitHub
  python3 scripts/check-doc-sync.py --root ..       # use local clones in ..

Exit code 0 when everything agrees, 1 when anything drifted, 2 on setup errors.
Standard library only. Set GITHUB_TOKEN to avoid API rate limits when fetching.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

ORG = "clever-cc-plugins"
WORDS = {0: "No", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five",
         6: "Six", 7: "Seven", 8: "Eight", 9: "Nine", 10: "Ten", 11: "Eleven",
         12: "Twelve"}


class Source:
    """Reads files and skill lists, either from local clones or from GitHub."""

    def __init__(self, root=None):
        self.root = root
        self.token = os.environ.get("GITHUB_TOKEN")

    def _get(self, url):
        headers = {"User-Agent": "check-doc-sync"}
        if self.token and "api.github.com" in url:
            headers["Authorization"] = "Bearer " + self.token
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
                return r.read().decode("utf-8")
        except urllib.error.URLError as e:
            raise SystemExit("error: cannot fetch %s: %s" % (url, e))

    def read(self, repo, path):
        if self.root:
            with open(os.path.join(self.root, repo, path), encoding="utf-8") as f:
                return f.read()
        return self._get("https://raw.githubusercontent.com/%s/%s/HEAD/%s" % (ORG, repo, path))

    def skills(self, repo, plugin):
        """Sorted skill names: directories under skills/ that hold a SKILL.md."""
        prefix = "plugins/%s/skills/" % plugin
        if self.root:
            base = os.path.join(self.root, repo, prefix)
            if not os.path.isdir(base):
                return []
            return sorted(d for d in os.listdir(base)
                          if os.path.isfile(os.path.join(base, d, "SKILL.md")))
        tree = json.loads(self._get(
            "https://api.github.com/repos/%s/%s/git/trees/HEAD?recursive=1" % (ORG, repo)))
        found = set()
        for item in tree.get("tree", []):
            m = re.fullmatch(re.escape(prefix) + r"([^/]+)/SKILL\.md", item["path"])
            if m:
                found.add(m.group(1))
        return sorted(found)


def slash_names(text, plugin):
    return set(re.findall(r"`/%s:([a-z0-9-]+)`" % re.escape(plugin), text))


def check(src, marketplace_json, marketplace_readme, profile_readme):
    """Returns a list of human-readable problems. Empty list means in sync."""
    problems = []
    plugins = [p["name"] for p in json.loads(marketplace_json)["plugins"]]
    skills = {}
    for name in plugins:
        skills[name] = src.skills(name, name)
    n_plugins = len(plugins)
    n_skills = sum(len(s) for s in skills.values())
    n_slash = sum(1 for s in skills.values() if s)
    n_hooks = n_plugins - n_slash

    # --- marketplace README -------------------------------------------------
    m = re.search(r"(\d+) plugins available", marketplace_readme)
    if not m:
        problems.append("marketplace README: no '<N> plugins available' line")
    elif int(m.group(1)) != n_plugins:
        problems.append("marketplace README: says %s plugins available, catalog has %d"
                        % (m.group(1), n_plugins))
    for name in plugins:
        if "/plugin install %s@%s" % (name, ORG) not in marketplace_readme:
            problems.append("marketplace README: no install line for %s" % name)
        row = next((l for l in marketplace_readme.splitlines()
                    if l.startswith("|") and "[`%s`](" % name in l), None)
        if row is None:
            problems.append("marketplace README: no table row for %s" % name)
        elif skills[name]:
            _diff(problems, "marketplace README row for %s" % name,
                  set(skills[name]), slash_names(row, name))

    # --- org profile README -------------------------------------------------
    where = "org profile README"
    for badge, expected in (("plugins", n_plugins), ("skills", n_skills)):
        m = re.search(r"badge/%s-(\d+)-" % badge, profile_readme)
        if not m:
            problems.append("%s: no %s badge" % (where, badge))
        elif int(m.group(1)) != expected:
            problems.append("%s: %s badge says %s, family has %d"
                            % (where, badge, m.group(1), expected))
    m = re.search(r"(\d+) plugins available", profile_readme)
    if m and int(m.group(1)) != n_plugins:
        problems.append("%s: install example says %s plugins available, catalog has %d"
                        % (where, m.group(1), n_plugins))
    m = re.search(r"(\w+) plugins ship `/slash` commands", profile_readme)
    if m and m.group(1) != WORDS.get(n_slash):
        problems.append("%s: says '%s plugins ship /slash commands', expected %s"
                        % (where, m.group(1), WORDS.get(n_slash, n_slash)))
    m = re.search(r"(\w+) (?:runs|run) automatically via hooks", profile_readme)
    if m and n_hooks != 1:
        problems.append("%s: text about hook-only plugins assumes one, found %d" % (where, n_hooks))
    for name in plugins:
        if "[**%s**](" % name not in profile_readme:
            problems.append("%s: plugin table has no row for %s" % (where, name))
        line = next((l for l in profile_readme.splitlines()
                     if l.startswith("- **%s**" % name)), None)
        if line is None:
            problems.append("%s: quick-start list has no line for %s" % (where, name))
            continue
        if not skills[name]:
            continue
        shown = slash_names(line, name)
        extra = re.search(r"\+(\d+) more", line)
        more = int(extra.group(1)) if extra else 0
        if not shown <= set(skills[name]):
            problems.append("%s: quick-start for %s names unknown skills: %s"
                            % (where, name, ", ".join(sorted(shown - set(skills[name])))))
        if len(shown) + more != len(skills[name]):
            problems.append("%s: quick-start for %s covers %d skills (%d shown + %d more), plugin has %d"
                            % (where, name, len(shown) + more, len(shown), more, len(skills[name])))

    # --- plugin READMEs -----------------------------------------------------
    for name in plugins:
        try:
            readme = src.read(name, "README.md")
        except OSError:
            problems.append("%s README: cannot read README.md" % name)
            continue
        if skills[name]:
            table = set()
            for line in readme.splitlines():
                m = re.match(r"\|\s*`/%s:([a-z0-9-]+)`" % re.escape(name), line)
                if m:
                    table.add(m.group(1))
            _diff(problems, "%s README skill table" % name, set(skills[name]), table)
        footer = readme[readme.rfind("<p align=\"center\">"):]
        for other in plugins:
            if other != name and "/%s/%s\"" % (ORG, other) not in footer:
                problems.append("%s README: footer does not link to %s" % (name, other))
    return problems


def _diff(problems, label, truth, documented):
    for s in sorted(truth - documented):
        problems.append("%s: missing /%s" % (label, s))
    for s in sorted(documented - truth):
        problems.append("%s: lists /%s, which no longer exists" % (label, s))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--root", help="directory holding local clones of every repo (marketplace, .github, cc-*)")
    args = ap.parse_args(argv)
    src = Source(args.root)
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        mj = open(os.path.join(here, ".claude-plugin", "marketplace.json"), encoding="utf-8").read()
        mr = open(os.path.join(here, "README.md"), encoding="utf-8").read()
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    try:
        profile = src.read(".github", "profile/README.md")
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    problems = check(src, mj, mr, profile)
    if problems:
        print("Documentation drift (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("Documentation is in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
