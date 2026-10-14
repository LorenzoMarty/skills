#!/usr/bin/env python3
"""Scan E_Mind vault for structural issues: orphan notes, Registros without a
linked hub, missing MOC entries, incomplete frontmatter, and duplicate-title
candidates. Prints a JSON report to stdout. Read-only — makes no changes.
"""
import json
import re
import sys
from pathlib import Path

VAULT = Path(r"C:/Users/loren/OneDrive/Desktop/E_Mind")
SCOPE_DIRS = ["01 - Notas Atômicas", "02 - Projetos", "03 - Trabalho", "05 - MOCs"]
MOC_PROJETOS = VAULT / "05 - MOCs" / "MOC - Projetos.md"
MOC_CONHECIMENTO = VAULT / "05 - MOCs" / "MOC - Conhecimento.md"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")


def strip_code(text: str) -> str:
    """Remove fenced/inline code so literal `[[...]]`-looking syntax in code
    (e.g. Cloudflare Pages' `[[path]].js` route files) isn't read as a wikilink.
    """
    text = FENCED_CODE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1")


def parse_frontmatter(text: str) -> dict:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm = {}
    last = None
    for line in m.group(1).splitlines():
        if line.lstrip().startswith("- ") and last and not fm[last]:
            fm[last] = "[block-list]"  # YAML block list: key has items below
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        last = key.strip()
        fm[last] = val.strip()
    return fm


def all_md_files():
    return [p for p in VAULT.rglob("*.md") if not any(part.startswith(".") for part in p.parts)]


def scope_md_files():
    out = []
    for d in SCOPE_DIRS:
        base = VAULT / d
        if base.exists():
            out.extend(base.rglob("*.md"))
    return out


def project_root(f: Path):
    """Top-level project folder for a file under 02 - Projetos / 03 - Trabalho,
    e.g. '03 - Trabalho/Qiron' for '03 - Trabalho/Qiron/Backend/Registros/x.md'.
    Returns None for files outside those two trees (or directly inside them).
    """
    rel = f.relative_to(VAULT).parts
    if rel[0] in ("02 - Projetos", "03 - Trabalho") and len(rel) > 1:
        return f"{rel[0]}/{rel[1]}"
    return None


def wikilink_targets(text: str):
    """Return the set of note *stems* a text links to. Wikilinks may be
    path-qualified (``[[Helix/Helix|Helix]]``) so take the last path segment.
    """
    out = set()
    for raw in WIKILINK_RE.findall(strip_code(text)):
        raw = raw.strip()
        stem = raw.split("/")[-1].strip()
        out.add(stem)
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    files = all_md_files()
    scope_files = scope_md_files()

    # backlink graph: note title (filename w/o .md) -> set of files linking to it
    backlinks = {}
    file_by_stem = {}
    for f in files:
        stem = f.stem
        file_by_stem.setdefault(stem, []).append(f)

    for f in files:
        text = read_text(f)
        for target in wikilink_targets(text):
            backlinks.setdefault(target, set()).add(str(f.relative_to(VAULT)))

    report = {
        "orphans": [],
        "registros_sem_hub": [],
        "moc_faltando": [],
        "frontmatter_incompleto": [],
        "duplicatas_candidatas": [],
        "links_quebrados": [],
        "registros_nao_listados_no_hub": [],
        "doc_contrato_faltando": [],
    }

    # 1. Orphans: scope files (excluding MOCs and Registros themselves) with no backlink
    for f in scope_files:
        if f.parent.name == "05 - MOCs" or f.parent.name == "Registros":
            continue
        stem = f.stem
        linkers = backlinks.get(stem, set())
        linkers.discard(str(f.relative_to(VAULT)))
        if not linkers:
            report["orphans"].append(str(f.relative_to(VAULT)))

    # 2. Registros sem hub linkado
    for f in scope_files:
        if f.parent.name != "Registros":
            continue
        text = read_text(f)
        fm = parse_frontmatter(text)
        projeto = fm.get("projeto", "")
        m = re.search(r"\[\[([^\]]+)\]\]", projeto)
        if not m:
            report["registros_sem_hub"].append({
                "arquivo": str(f.relative_to(VAULT)),
                "problema": "frontmatter 'projeto' ausente ou sem [[link]]",
            })
            continue
        hub_name = m.group(1).strip().split("/")[-1].strip()
        hub_candidates = file_by_stem.get(hub_name, [])
        if not hub_candidates:
            report["registros_sem_hub"].append({
                "arquivo": str(f.relative_to(VAULT)),
                "problema": f"hub '[[{hub_name}]]' não existe como nota no vault",
            })
            continue

        # pasta errada: o Registro deveria estar dentro da árvore do projeto do
        # hub que ele declara em `projeto:` (mesmo top-level em 02/03), não em
        # outra pasta de projeto.
        registro_root = project_root(f)
        hub_roots = {project_root(c) for c in hub_candidates}
        if registro_root and hub_roots and registro_root not in hub_roots and None not in hub_roots:
            report["registros_sem_hub"].append({
                "arquivo": str(f.relative_to(VAULT)),
                "problema": (
                    f"pasta errada: registro está em '{registro_root}' mas hub "
                    f"'[[{hub_name}]]' vive em '{sorted(hub_roots)[0]}'"
                ),
            })

    # 3. MOC faltando: hubs em 02/03 e notas atômicas em 01, checar se MOC correspondente linka
    moc_proj_text = read_text(MOC_PROJETOS) if MOC_PROJETOS.exists() else ""
    # conhecimento é dividido em hubs temáticos ("MOC - Backend e IA" etc.); vale link em qualquer um
    moc_conh_text = chr(10).join(read_text(m) for m in MOC_CONHECIMENTO.parent.glob("MOC - *.md") if m.name != "MOC - Projetos.md")
    moc_proj_links = wikilink_targets(moc_proj_text)
    moc_conh_links = wikilink_targets(moc_conh_text)

    for base_dir, moc_links, moc_path in (
        (VAULT / "02 - Projetos", moc_proj_links, MOC_PROJETOS),
        (VAULT / "03 - Trabalho", moc_proj_links, MOC_PROJETOS),
    ):
        if not base_dir.exists():
            continue
        for sub in base_dir.iterdir():
            if not sub.is_dir():
                continue
            # hub file: same name as folder, or any top-level .md in the folder
            candidates = list(sub.glob("*.md"))
            hub_stems = {c.stem for c in candidates}
            if not hub_stems & moc_links:
                report["moc_faltando"].append({
                    "tipo": "projeto",
                    "pasta": str(sub.relative_to(VAULT)),
                    "moc": str(moc_path.relative_to(VAULT)),
                })

    atomicas_dir = VAULT / "01 - Notas Atômicas"
    if atomicas_dir.exists():
        for f in atomicas_dir.glob("*.md"):
            if f.stem not in moc_conh_links:
                report["moc_faltando"].append({
                    "tipo": "nota_atomica",
                    "arquivo": str(f.relative_to(VAULT)),
                    "moc": str(MOC_CONHECIMENTO.relative_to(VAULT)),
                })

    # 4. Frontmatter incompleto
    for f in scope_files:
        text = read_text(f)
        fm = parse_frontmatter(text)
        if not fm:
            report["frontmatter_incompleto"].append({
                "arquivo": str(f.relative_to(VAULT)),
                "faltando": "frontmatter ausente",
            })
            continue
        if f.parent.name == "Registros":
            required = ["criado", "tipo", "projeto", "tags"]
        else:
            required = ["criado", "status", "tags"]
        missing = [k for k in required if k not in fm or not fm[k]]
        if missing:
            report["frontmatter_incompleto"].append({
                "arquivo": str(f.relative_to(VAULT)),
                "faltando": missing,
            })

    # 5. Duplicatas candidatas: nomes normalizados iguais na mesma pasta
    from collections import defaultdict
    by_folder_norm = defaultdict(list)
    for f in scope_files:
        norm = re.sub(r"[^a-z0-9]", "", f.stem.lower())
        by_folder_norm[(str(f.parent), norm)].append(str(f.relative_to(VAULT)))
    for (_, norm), group in by_folder_norm.items():
        if len(group) > 1:
            report["duplicatas_candidatas"].append(group)

    # 6. Links quebrados: [[alvo]] cujo alvo não existe como arquivo em lugar nenhum do vault
    for f in scope_files:
        text = read_text(f)
        for target in wikilink_targets(text):
            if target not in file_by_stem:
                report["links_quebrados"].append({
                    "arquivo": str(f.relative_to(VAULT)),
                    "link_quebrado": target,
                })

    # 7. Registros não listados no hub: frontmatter aponta pra um hub válido
    # (já passou pela checagem 2), mas o hub não tem um [[link]] de volta pro
    # registro em nenhum lugar do seu texto (Log/tabela de Registros).
    for f in scope_files:
        if f.parent.name != "Registros":
            continue
        text = read_text(f)
        fm = parse_frontmatter(text)
        projeto = fm.get("projeto", "")
        m = re.search(r"\[\[([^\]]+)\]\]", projeto)
        if not m:
            continue  # já reportado em registros_sem_hub
        hub_name = m.group(1).strip().split("/")[-1].strip()
        hub_candidates = file_by_stem.get(hub_name, [])
        if not hub_candidates:
            continue  # já reportado em registros_sem_hub
        registro_stem = f.stem
        linked_by = backlinks.get(registro_stem, set())
        hub_paths = {str(c.relative_to(VAULT)) for c in hub_candidates}
        if not (linked_by & hub_paths):
            report["registros_nao_listados_no_hub"].append({
                "arquivo": str(f.relative_to(VAULT)),
                "hub": sorted(hub_paths)[0],
            })

    # 8. Documentos do contrato faltando: cada projeto em 02 - Projetos/03 -
    # Trabalho deve ter, em algum lugar da própria árvore (permite sub-hubs
    # tipo Qiron/Frontend + Qiron/Backend), Arquitetura.md, Decisões.md e uma
    # pasta Registros/.
    for base_dir in (VAULT / "02 - Projetos", VAULT / "03 - Trabalho"):
        if not base_dir.exists():
            continue
        for sub in base_dir.iterdir():
            if not sub.is_dir():
                continue
            hub_candidates = [
                c for c in sub.glob("*.md") if c.stem not in ("Arquitetura", "Decisões")
            ]
            if not hub_candidates:
                continue  # pasta sem hub próprio, nada a checar aqui
            faltando = []
            if not list(sub.rglob("Arquitetura.md")):
                faltando.append("Arquitetura.md")
            if not list(sub.rglob("Decisões.md")):
                faltando.append("Decisões.md")
            if not any(p.is_dir() for p in sub.rglob("Registros")):
                faltando.append("Registros/")
            if faltando:
                report["doc_contrato_faltando"].append({
                    "projeto": str(sub.relative_to(VAULT)),
                    "hub": str(sorted(hub_candidates)[0].relative_to(VAULT)),
                    "faltando": faltando,
                })

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
