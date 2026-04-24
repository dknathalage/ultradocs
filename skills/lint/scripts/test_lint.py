import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parent / "lint.py"


def run(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


def test_usage_error_on_missing_wiki_root():
    result = run(["/nonexistent/path"])
    assert result.returncode == 2


def test_clean_empty_wiki_exits_zero():
    with tempfile.TemporaryDirectory() as d:
        wiki = Path(d)
        (wiki / "refs").mkdir()
        (wiki / "topics").mkdir()
        (wiki / "overviews").mkdir()
        result = run([str(wiki)])
        assert result.returncode == 0, result.stderr
        out = json.loads(result.stdout)
        assert out["pages_scanned"] == 0
        assert out["defects"] == []


# ---------------------------------------------------------------------------
# unittest discovery shim — wraps all module-level test_* functions
# ---------------------------------------------------------------------------
def load_tests(loader, tests, pattern):
    import types
    module = sys.modules[__name__]
    for name in sorted(vars(module)):
        if name.startswith("test_") and callable(getattr(module, name)):
            fn = getattr(module, name)
            if not isinstance(fn, type):
                tests.addTest(unittest.FunctionTestCase(fn))
    return tests


if __name__ == "__main__":
    unittest.main()
