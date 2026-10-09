"""Every test in this directory runs in the pipeline.

The pipeline runs `python3 -m unittest discover`, which finds only the
methods of unittest.TestCase classes. A test written as a bare module
function is skipped without a word, and the step stays green. Twelve
were, the tests of the checks D-035, D-037, and D-039 added, from
October 4 until October 8, 2026 (D-041).
"""

import ast
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


class EveryTestRuns(unittest.TestCase):
    def test_no_test_is_a_bare_function(self) -> None:
        bare = [
            f"{path.name}:{node.lineno} {node.name}"
            for path in sorted(HERE.glob("test_*.py"))
            for node in ast.parse(path.read_text()).body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test")
        ]
        self.assertEqual(bare, [], "unittest skips these without a word; put each in a TestCase class")
