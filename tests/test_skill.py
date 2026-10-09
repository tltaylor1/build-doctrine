"""The plugin and its skills answer to the files they name.

A skill is a procedure an agent follows, so a path or a flag that no
longer exists sends the agent somewhere that is not there. The plugin
manifests carry the fields the Claude Code plugin reference requires,
every ${CLAUDE_PLUGIN_ROOT} path a skill names exists in this
repository, every flag a skill passes to a script is one the script
accepts, and each skill's name matches its directory (D-043).
"""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
PATH = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")


def frontmatter(text: str) -> dict[str, str]:
    head = text.split("---\n")[1]
    return dict(line.split(": ", 1) for line in head.splitlines() if ": " in line)


class Plugin(unittest.TestCase):
    def test_the_manifests_carry_the_required_fields(self) -> None:
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        self.assertTrue(market["name"] and market["owner"]["name"])
        self.assertEqual([p["name"] for p in market["plugins"]], [plugin["name"]])
        self.assertEqual(market["plugins"][0]["source"], ".")
        self.assertNotIn("version", plugin)

    def test_there_is_a_skill(self) -> None:
        self.assertTrue(SKILLS)

    def test_each_skill_is_named_for_its_directory_and_described(self) -> None:
        for path in SKILLS:
            meta = frontmatter(path.read_text())
            self.assertEqual(meta.get("name"), path.parent.name)
            self.assertTrue(0 < len(meta.get("description", "")) <= 1536)

    def test_every_path_a_skill_names_exists(self) -> None:
        for path in SKILLS:
            for target in PATH.findall(path.read_text()):
                self.assertTrue((ROOT / target).exists(), f"{path.parent.name} names {target}")

    def test_every_flag_passed_to_a_script_is_accepted(self) -> None:
        for path in SKILLS:
            for script, args in re.findall(r"scripts/([a-z_]+\.py) ([^\n`]*)", path.read_text()):
                source = (ROOT / "scripts" / script).read_text()
                for flag in re.findall(r"(--[a-z-]+)", args):
                    self.assertTrue(f'"{flag}"' in source, f"{path.parent.name} passes {flag} to {script}")
