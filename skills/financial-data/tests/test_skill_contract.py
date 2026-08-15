from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_skill_entrypoint_is_discoverable_and_compact():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: financial-data\n")
    match = re.search(r"^description:\s*(.+)$", text, re.M)
    assert match and match.group(1).startswith("Use when")
    body = text.split("---", 2)[-1]
    assert len(body.split()) < 650
    assert "SOURCE_CONFLICT" in body
    assert "references/" in body


def test_required_reference_modules_exist():
    expected = {
        "data-contract.md", "instrument-master.md", "source-registry.md", "source-routing.md",
        "validation-rules.md", "market-conventions.md", "compliance.md", "fallback-policy.md",
        "workflows.md", "a-share.md", "us-hk.md", "macro-rates.md", "futures-commodities.md", "derivatives.md",
    }
    actual = {p.name for p in (ROOT / "references").glob("*.md")}
    assert expected <= actual


def test_readme_separates_implemented_from_registry_only_sources():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Implemented in v0.1.0" in text
    assert "Registry / reference only" in text
    assert "SEC_CONTACT" in text
    assert "simonlin1212/a-stock-data" in text
    assert "simonlin1212/global-stock-data" in text


def test_agent_metadata_exists():
    text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert 'display_name: "financial-data"' in text
    assert "default_prompt:" in text
