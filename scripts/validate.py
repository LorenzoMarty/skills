#!/usr/bin/env python3
"""Valida a estrutura do marketplace, dos plugins e das skills.

Uso: python3 scripts/validate.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors: list[str] = []


def error(msg: str) -> None:
    errors.append(msg)


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        error(f"{path.relative_to(ROOT)}: arquivo não encontrado")
    except json.JSONDecodeError as exc:
        error(f"{path.relative_to(ROOT)}: JSON inválido ({exc})")
    return None


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    current = None
    for line in text[4:end].splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            current = match.group(1)
            value = match.group(2).strip()
            # Blocos ">-" / "|" continuam nas linhas indentadas seguintes.
            fields[current] = "" if value in (">", ">-", "|", "|-") else value.strip("'\"")
        elif current and line.startswith((" ", "\t")):
            fields[current] = (fields[current] + " " + line.strip()).strip()
    return fields


def check_skill(skill_dir: Path, seen: dict[str, Path]) -> None:
    rel = skill_dir.relative_to(ROOT)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        error(f"{rel}: falta SKILL.md")
        return
    meta = parse_frontmatter(skill_md)
    if meta is None:
        error(f"{rel}/SKILL.md: frontmatter YAML ausente ou mal fechado")
        return
    name = meta.get("name", "")
    description = meta.get("description", "")
    if not name:
        error(f"{rel}/SKILL.md: campo 'name' ausente")
    elif name != skill_dir.name:
        error(f"{rel}/SKILL.md: name '{name}' difere do nome da pasta '{skill_dir.name}'")
    elif not NAME_RE.match(name) or len(name) > 64:
        error(f"{rel}/SKILL.md: name '{name}' deve ser kebab-case com até 64 caracteres")
    if not description:
        error(f"{rel}/SKILL.md: campo 'description' ausente")
    elif len(description) > 1024:
        error(f"{rel}/SKILL.md: description com {len(description)} caracteres (máx. 1024)")
    if name in seen:
        error(f"{rel}: skill '{name}' duplicada (também em {seen[name].relative_to(ROOT)})")
    else:
        seen[name] = skill_dir


def main() -> int:
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if marketplace is None:
        return report()

    listed: set[Path] = set()
    names: set[str] = set()
    seen_skills: dict[str, Path] = {}
    for entry in marketplace.get("plugins", []):
        name = entry.get("name", "")
        if name in names:
            error(f"marketplace.json: plugin '{name}' listado mais de uma vez")
        names.add(name)
        source = (ROOT / entry.get("source", "")).resolve()
        listed.add(source)
        if not source.is_dir():
            error(f"marketplace.json: source do plugin '{name}' não existe ({entry.get('source')})")
            continue
        manifest = load_json(source / ".claude-plugin" / "plugin.json")
        if manifest and manifest.get("name") != name:
            error(f"{source.relative_to(ROOT)}: plugin.json name '{manifest.get('name')}' difere de '{name}'")
        skills_dir = source / "skills"
        if skills_dir.is_dir():
            for skill_dir in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
                check_skill(skill_dir, seen_skills)

    for plugin_dir in sorted((ROOT / "plugins").iterdir()):
        if plugin_dir.is_dir() and plugin_dir.resolve() not in listed:
            error(f"{plugin_dir.relative_to(ROOT)}: plugin fora do marketplace.json")

    return report(len(seen_skills), len(names))


def report(skills: int = 0, plugins: int = 0) -> int:
    if errors:
        for msg in errors:
            print(f"✗ {msg}")
        print(f"\n{len(errors)} erro(s).")
        return 1
    print(f"✓ {plugins} plugin(s), {skills} skill(s) válidos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
