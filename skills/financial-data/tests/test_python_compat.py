from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "scripts" / "financial_data"
PEP604_ANNOTATION = re.compile(r"(?:\b[A-Za-z_]\w*(?:\[[^\n]*?\])?|\])\s*\|\s*(?:None|[A-Za-z_])")


def test_core_package_avoids_python310_union_syntax():
    failures = []
    for path in sorted(PACKAGE.rglob("*.py")):
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PEP604_ANNOTATION.search(line):
                failures.append(f"{path.relative_to(ROOT)}:{lineno}: {line.strip()}")
    assert not failures, "Python 3.10+ union syntax found; core promises Python 3.9+:\n" + "\n".join(failures)
