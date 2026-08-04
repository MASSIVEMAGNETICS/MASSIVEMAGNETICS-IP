from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .object_store import load_object


def _load_all_inventions(root: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for view_path in sorted((root / "views" / "inventions").glob("MMIP-*.json")):
        view = json.loads(view_path.read_text(encoding="utf-8"))
        record = load_object(root, view["object_sha256"])
        records[record["invention_id"]] = record
    return records


def build_graph(root: Path) -> tuple[dict[str, str], set[tuple[str, str, str]]]:
    records = _load_all_inventions(root)
    nodes = {identifier: record["title"] for identifier, record in records.items()}
    edges: set[tuple[str, str, str]] = set()
    for identifier, record in records.items():
        lineage = record.get("lineage", {})
        for parent in lineage.get("parent_inventions", []):
            edges.add((parent, identifier, "parent"))
        for child in lineage.get("child_inventions", []):
            edges.add((identifier, child, "parent"))
        for old in lineage.get("supersedes", []):
            edges.add((old, identifier, "superseded by"))
    return nodes, edges


def _detect_cycle(nodes: dict[str, str], edges: set[tuple[str, str, str]]) -> None:
    adjacency: dict[str, list[str]] = {node: [] for node in nodes}
    for source, target, _ in edges:
        adjacency.setdefault(source, []).append(target)
        adjacency.setdefault(target, [])
    visiting: set[str] = set()
    visited: set[str] = set()

    def walk(node: str) -> None:
        if node in visiting:
            raise ValueError(f"lineage cycle detected at {node}")
        if node in visited:
            return
        visiting.add(node)
        for child in adjacency[node]:
            walk(child)
        visiting.remove(node)
        visited.add(node)

    for node in sorted(adjacency):
        walk(node)


def render_mermaid(root: Path) -> str:
    nodes, edges = build_graph(root)
    _detect_cycle(nodes, edges)
    identifiers = {identifier: "n" + re.sub(r"[^A-Za-z0-9_]", "_", identifier) for identifier in nodes}
    lines = ["flowchart TD"]
    for identifier, title in sorted(nodes.items()):
        label = f"{identifier}: {title}".replace('"', "'")
        lines.append(f'    {identifiers[identifier]}["{label}"]')
    for source, target, relation in sorted(edges):
        if source not in identifiers:
            identifiers[source] = "n" + re.sub(r"[^A-Za-z0-9_]", "_", source)
            lines.append(f'    {identifiers[source]}["{source}: external/unknown"]')
        if target not in identifiers:
            identifiers[target] = "n" + re.sub(r"[^A-Za-z0-9_]", "_", target)
            lines.append(f'    {identifiers[target]}["{target}: external/unknown"]')
        lines.append(f'    {identifiers[source]} -->|"{relation}"| {identifiers[target]}')
    return "\n".join(lines) + "\n"

