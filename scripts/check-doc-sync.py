#!/usr/bin/env python3
"""Check that plugin and skill documentation across the plugin family agrees.

Source of truth: each plugin repo's plugins/<name>/skills/<skill>/SKILL.md on
its default branch, plus the plugin list in .claude-plugin/marketplace.json.

Checked against that truth:
  - marketplace README: plugin count, one install line per plugin, skills per row
  - org profile README (.github): plugin and skill badges, "+N more" counts,
    "<N> plugins ship /slash commands", plugin table, install-example count
  - every plugin README: skill table rows, footer links to the other plugins
  - every plugin with skills: skills/_shared/learnings-protocol.md exists and is identical across plugins

Usage:
  python3 scripts/check-doc-sync.py                 # fetch from GitHub
  python3 scripts/check-doc-sync.py --root ..       # plugin repos and .github from local clones in ..
                                                    # (marketplace README and catalog always come from this checkout)

Exit code 0 when everything agrees, 1 when anything drifted, 2 when the check
could not run (network failure, rate limit, truncated API answer, missing file).
Standard library only. Set GITHUB_TOKEN to avoid API rate limits when fetching.
"""
import argparse
import collections
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ORG = "clever-cc-plugins"
WORDS = ["no", "one", "two", "three", "four", "five", "six", "seven", "eight",
         "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
         "sixteen", "seventeen", "eighteen", "nineteen", "twenty"]


def count_matches(text, n):
    """True when text is the number n, as digits or as an English word."""
    t = text.strip().lower()
    return t == str(n) or (n < len(WORDS) and t == WORDS[n])


class Source:
    """Reads files and skill lists, either from local clones or from GitHub."""

    def __init__(self, root=None):
        self.root = root
        self.token = os.environ.get("GITHUB_TOKEN")
        self.retry_delay = 3
        # Only the API call sends the token; raw.githubusercontent.com is
        # fetched anonymously, so every repo in the family must stay public.

    def _get(self, url):
        """GET with one retry. A 404 raises FileNotFoundError, anything else OSError."""
        headers = {"User-Agent": "check-doc-sync"}
        if self.token and "api.github.com" in url:
            headers["Authorization"] = "Bearer " + self.token
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as r:
                    return r.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise FileNotFoundError("404 for %s" % url)
                if attempt == 2:
                    raise OSError("cannot fetch %s: HTTP %s" % (url, e.code))
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 2:
                    raise OSError("cannot fetch %s: %s" % (url, e))
            time.sleep(self.retry_delay)
        raise OSError("cannot fetch %s" % url)  # unreachable; keeps the flow explicit

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
        if tree.get("truncated"):
            raise OSError("GitHub tree for %s is truncated; cannot list skills reliably" % repo)
        found = set()
        for item in tree.get("tree", []):
            m = re.fullmatch(re.escape(prefix) + r"([^/]+)/SKILL\.md", item["path"])
            if m:
                found.add(m.group(1))
        return sorted(found)


def repo_of(entry):
    """Repo name from the entry's git-subdir URL, falling back to the plugin name."""
    source = entry.get("source")
    url = source.get("url", "") if isinstance(source, dict) else ""
    m = re.search(r"github\.com/[^/]+/([^/]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else entry["name"]


def slash_names(text, plugin):
    return set(re.findall(r"`/%s:([a-z0-9-]+)`" % re.escape(plugin), text))


def check(src, marketplace_json, marketplace_readme, profile_readme):
    """Returns a list of human-readable problems. Empty list means in sync."""
    problems = []
    entries = json.loads(marketplace_json)["plugins"]
    plugins = [p["name"] for p in entries]
    repo = {p["name"]: repo_of(p) for p in entries}
    skills = {}
    for name in plugins:
        skills[name] = src.skills(repo[name], name)
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
        else:
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
    if not m:
        problems.append("%s: no '<N> plugins available' line in the install example" % where)
    elif int(m.group(1)) != n_plugins:
        problems.append("%s: install example says %s plugins available, catalog has %d"
                        % (where, m.group(1), n_plugins))
    m = re.search(r"(\w+) plugins ship `/slash` commands", profile_readme)
    if not m:
        problems.append("%s: no '<N> plugins ship /slash commands' sentence" % where)
    elif not count_matches(m.group(1), n_slash):
        problems.append("%s: says '%s plugins ship /slash commands', expected %d"
                        % (where, m.group(1), n_slash))
    # The profile text says "one runs automatically via hooks"; that sentence
    # needs rewording if the number of hook-only plugins ever changes.
    if "runs automatically via hooks" in profile_readme and n_hooks != 1:
        problems.append("%s: text says one plugin runs via hooks, found %d" % (where, n_hooks))
    for name in plugins:
        if not any(l.startswith("|") and "[**%s**](" % name in l
                   for l in profile_readme.splitlines()):
            problems.append("%s: plugin table has no row for %s" % (where, name))
        line = next((l for l in profile_readme.splitlines()
                     if l.startswith("- **%s**" % name)), None)
        if line is None:
            problems.append("%s: quick-start list has no line for %s" % (where, name))
            continue
        shown = slash_names(line, name)
        if not skills[name]:
            if shown:
                problems.append("%s: quick-start for %s lists skills, but none were found in its repo"
                                % (where, name))
            continue
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
            readme = src.read(repo[name], "README.md")
        except FileNotFoundError:
            problems.append("%s README: README.md not found" % name)
            continue
        table = set()
        for line in readme.splitlines():
            m = re.match(r"\|\s*`/%s:([a-z0-9-]+)`" % re.escape(name), line)
            if m:
                table.add(m.group(1))
        # An empty source list with a documented table means the lookup is
        # wrong (path, rename), not that the plugin is hook-only.
        _diff(problems, "%s README skill table" % name, set(skills[name]), table)
        start = readme.rfind("<p align=\"center\">")
        if start < 0:
            problems.append("%s README: no footer found" % name)
            continue
        footer = readme[start:]
        for other in plugins:
            if other != name and not re.search(
                    r"github\.com/%s/%s(?![\w-])" % (re.escape(ORG), re.escape(repo[other])), footer):
                problems.append("%s README: footer does not link to %s" % (name, other))
    problems.extend(check_learnings_protocol(src, plugins, repo, skills))
    return problems


def check_learnings_protocol(src, plugins, repo, skills):
    """Every plugin with skills ships the same learnings-protocol.md; the most common text is the reference."""
    problems = []
    texts = {}
    for name in plugins:
        if not skills[name]:
            continue
        path = "plugins/%s/skills/_shared/learnings-protocol.md" % name
        try:
            texts[name] = src.read(repo[name], path)
        except FileNotFoundError:
            problems.append("%s: %s not found" % (name, path))
    if texts:
        reference = collections.Counter(texts.values()).most_common(1)[0][0]
        holders = ", ".join(n for n, t in texts.items() if t == reference)
        for name, text in texts.items():
            if text != reference:
                problems.append("%s: _shared/learnings-protocol.md differs from the copy in %s (%s)"
                                % (name, holders, _describe_difference(reference, text)))
    return problems


def _describe_difference(a, b):
    """Where a and b first differ: a line number, or a note when only line endings or the final newline differ."""
    a_lines, b_lines = a.splitlines(), b.splitlines()
    for i, (x, y) in enumerate(zip(a_lines, b_lines), 1):
        if x != y:
            return "first difference at line %d" % i
    if len(a_lines) == len(b_lines):
        return "only line endings or the final newline differ"
    return "first difference at line %d" % (min(len(a_lines), len(b_lines)) + 1)


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
        with open(os.path.join(here, ".claude-plugin", "marketplace.json"), encoding="utf-8") as f:
            mj = f.read()
        with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
            mr = f.read()
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    try:
        profile = src.read(".github", "profile/README.md")
        problems = check(src, mj, mr, profile)
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if problems:
        print("Documentation drift (%d):" % len(problems))
        for p in problems:
            print("  - " + p)
        return 1
    print("Documentation is in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
