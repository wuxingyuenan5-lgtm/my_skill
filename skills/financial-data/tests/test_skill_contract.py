from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def test_skill_entrypoint_is_discoverable_compact_and_navigation_first():
    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: financial-data\n")
    match = re.search(r"^description:\s*(.+)$", text, re.M)
    assert match and match.group(1).startswith("Use when")
    body = text.split("---", 2)[-1]
    assert len(body.split()) < 1100
    assert "NAVIGATION.md" in body
    assert "Do not read the full capability index" in body
    assert "providers/" in body and "datasets/" in body and "tasks/" in body
    assert "references/" in body


def test_required_reference_modules_exist():
    expected = {
        "data-contract.md", "instrument-master.md", "source-registry.md", "source-routing.md",
        "validation-rules.md", "market-conventions.md", "compliance.md", "fallback-policy.md",
        "workflows.md", "a-share.md", "us-hk.md", "macro-rates.md", "futures-commodities.md", "derivatives.md",
    }
    actual = {p.name for p in (ROOT / "references").glob("*.md")}
    assert expected <= actual


def test_readme_declares_encyclopedia_first_and_reference_runtime_role():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "0.3 encyclopedia-first" in text
    assert "NAVIGATION.md" in text
    assert "Downstream projects are not expected to depend on this Skill at runtime" in text
    assert "references/capability-index.yaml" in text


def test_agent_metadata_exists():
    text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    assert 'display_name: "financial-data"' in text
    assert "default_prompt:" in text
