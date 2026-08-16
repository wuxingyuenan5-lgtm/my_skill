from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
NAV = ROOT / "NAVIGATION.md"

PROVIDER_SECTIONS = [
    "## Identity",
    "## Access and authentication",
    "## Technical request limits",
    "## Data-range limits",
    "## Freshness and publication timing",
    "## Licensing and redistribution",
    "## Data-quality limitations",
    "## Copy guidance",
]


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_skill_uses_navigation_as_default_entrypoint():
    skill = _text(ROOT / "SKILL.md")
    assert "NAVIGATION.md" in skill
    assert "Search `references/capability-index.yaml` first" not in skill
    assert "Do not read the full capability index" in skill


def test_navigation_exists_and_all_local_markdown_targets_exist():
    assert NAV.exists()
    text = _text(NAV)
    targets = set(re.findall(r"`((?:tasks|datasets|providers|references)/[^`]+\.md|references/capability-index\.yaml)`", text))
    assert targets, "NAVIGATION.md must contain routed local targets"
    missing = [target for target in sorted(targets) if not (ROOT / target).exists()]
    assert not missing, f"missing navigation targets: {missing}"


def test_provider_cards_follow_source_constraint_contract():
    provider_dir = ROOT / "providers"
    assert provider_dir.exists()
    cards = sorted(provider_dir.glob("*.md"))
    assert cards, "provider cards must exist"
    for card in cards:
        text = _text(card)
        assert "last_verified:" in text, card.name
        for section in PROVIDER_SECTIONS:
            assert section in text, f"{card.name} missing {section}"
        assert "TBD" not in text and "TODO" not in text, card.name


def test_new_navigation_cards_have_no_placeholders():
    paths = [NAV]
    for dirname in ("tasks", "datasets", "providers"):
        base = ROOT / dirname
        if base.exists():
            paths.extend(base.rglob("*.md"))
    for path in paths:
        if not path.exists():
            continue
        text = _text(path)
        assert "TBD" not in text and "TODO" not in text, str(path.relative_to(ROOT))


def test_readme_declares_encyclopedia_first_and_downstream_independence():
    readme = _text(ROOT / "README.md")
    assert "0.3 encyclopedia-first" in readme
    assert "Downstream projects are not expected to depend on this Skill at runtime" in readme
