from __future__ import annotations

from typing import Any, Iterable, Mapping


def _dedupe(values: Iterable[str]) -> list[str]:
    out, seen = [], set()
    for value in values:
        if value and value not in seen:
            seen.add(value); out.append(value)
    return out


def build_project_manifest(capability_index: Mapping[str, Any], selected_ids: Iterable[str], *, project_name: str = "project") -> dict[str, Any]:
    """Build a freeze/copy manifest for capabilities selected from the handbook."""
    capabilities = capability_index.get("capabilities") or []
    by_id = {str(item["id"]): dict(item) for item in capabilities}
    selected = []
    for capability_id in selected_ids:
        key = str(capability_id)
        if key not in by_id:
            raise KeyError(f"Unknown capability id: {key}")
        selected.append(by_id[key])
    primary = _dedupe(s for item in selected for s in (item.get("primary_sources") or []))
    fallback = _dedupe(s for item in selected for s in (item.get("fallback_sources") or []))
    refs = _dedupe(str(item.get("reference") or "") for item in selected)
    runtime = _dedupe(str(item.get("runtime") or "") for item in selected)
    auth = _dedupe(str(item.get("auth") or "") for item in selected if str(item.get("auth") or "") not in {"", "none"})
    restricted = [str(item["id"]) for item in selected if str(item.get("status")) == "RESTRICTED"]
    return {"project_name":project_name,"capabilities":selected,"capability_ids":[str(i["id"]) for i in selected],"primary_sources":primary,"fallback_sources":fallback,"references":refs,"runtime_modules":runtime,"auth_requirements":auth,"restricted_capabilities":restricted,"freeze_policy":"copy selected recipes/modules into the downstream project and maintain them there"}


def render_manifest_markdown(manifest: Mapping[str, Any]) -> str:
    name = str(manifest.get("project_name") or "project")
    lines = [f"# {name} data pack","","Generated from the financial-data handbook. Freeze only the capabilities this project needs.","","## Capabilities"]
    lines += [f"- `{x}`" for x in (manifest.get("capability_ids") or [])]
    lines += ["","## Primary sources"] + [f"- `{x}`" for x in (manifest.get("primary_sources") or [])]
    if manifest.get("fallback_sources"):
        lines += ["","## Fallback sources"] + [f"- `{x}`" for x in manifest.get("fallback_sources")]
    if manifest.get("references"):
        lines += ["","## Handbook references"] + [f"- `{x}`" for x in manifest.get("references")]
    if manifest.get("restricted_capabilities"):
        lines += ["","## Restricted / licensed capabilities"] + [f"- `{x}`" for x in manifest.get("restricted_capabilities")]
    lines += ["","## Maintenance rule","Re-check provider terms, endpoint health, field mappings and last_verified before major releases."]
    return "\n".join(lines)+"\n"
