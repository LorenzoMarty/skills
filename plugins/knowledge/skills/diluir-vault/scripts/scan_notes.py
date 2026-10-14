#!/usr/bin/env python3
"""Scanner só-leitura pra skill diluir-vault.

Varre o vault E_Mind e devolve candidatas a:
- diluir (nota atômica longa/redundante, ou registro/hub cru que já virou padrão reusável)
- padronizar (frontmatter ou estrutura de seções fora do template)
- agrupar (notas atômicas com sobreposição forte de tema/tags — candidatas a merge)

Não escreve nada. Toda decisão de aplicar é do Claude, guiado pelo relatório.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

VAULT = Path("C:/Users/loren/OneDrive/Desktop/E_Mind")
SCOPE_DIRS = [
    "01 - Notas Atômicas",
    "02 - Projetos",
    "03 - Trabalho",
    "05 - MOCs",
]
EXCLUDE_DIRS = {"06 - Templates", "08 - Claude"}

TEMPLATE_SECTIONS = ["Ideia central", "Desenvolvimento", "Conexões", "Fonte"]
TEMPLATE_FRONTMATTER_KEYS = ["criado", "tags", "status", "area"]

LONG_NOTE_WORDS = 550  # nota atômica acima disso é candidata a diluir/dividir
STOPWORDS = {
    "de", "da", "do", "das", "dos", "e", "a", "o", "as", "os", "em", "com",
    "para", "por", "que", "um", "uma", "no", "na", "nos", "nas", "se", "ao",
    "aos", "às", "à", "como", "sem", "não", "mais", "já", "é", "ou",
}


def iter_md_files():
    for d in SCOPE_DIRS:
        base = VAULT / d
        if not base.exists():
            continue
        for p in base.rglob("*.md"):
            if any(part in EXCLUDE_DIRS for part in p.parts):
                continue
            yield p


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fm_raw = text[3:end].strip("\n")
    body = text[end + 4:]
    fm = {}
    for line in fm_raw.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, body


def word_count(text):
    return len(re.findall(r"\w+", text))


def keywords(title, tags_str):
    words = set(re.findall(r"[a-zà-ú0-9]+", title.lower()))
    words |= {t.strip().strip("[]").lower() for t in tags_str.split(",") if t.strip()}
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def main():
    notas_atomicas = []
    registros = []
    all_files = {}

    for p in iter_md_files():
        try:
            text = p.read_text(encoding="utf-8")
        except Exception as e:
            all_files[str(p)] = {"error": str(e)}
            continue
        fm, body = parse_frontmatter(text)
        all_files[str(p)] = {"fm": fm, "body": body}
        if "01 - Notas Atômicas" in p.parts:
            notas_atomicas.append((p, fm, body, text))
        elif "Registros" in p.parts:
            registros.append((p, fm, body, text))

    result = {
        "notas_longas": [],
        "fora_padrao": [],
        "grupos_sobrepostos": [],
        "registros_destilaveis": [],
    }

    # 1. notas longas (candidata a diluir/dividir)
    for p, fm, body, text in notas_atomicas:
        wc = word_count(body)
        if wc > LONG_NOTE_WORDS:
            result["notas_longas"].append({
                "arquivo": str(p),
                "palavras": wc,
                "limite": LONG_NOTE_WORDS,
            })

    # 2. fora do padrão (frontmatter incompleto ou seções faltando/fora de ordem)
    for p, fm, body, text in notas_atomicas:
        problemas = []
        faltando_fm = [k for k in TEMPLATE_FRONTMATTER_KEYS if k not in fm]
        if faltando_fm:
            problemas.append(f"frontmatter sem: {', '.join(faltando_fm)}")
        secoes_presentes = re.findall(r"^##\s+(.+)$", body, flags=re.MULTILINE)
        secoes_presentes = [s.strip() for s in secoes_presentes]
        faltando_secoes = [s for s in TEMPLATE_SECTIONS if s not in secoes_presentes]
        if faltando_secoes:
            problemas.append(f"seções sem: {', '.join(faltando_secoes)}")
        if problemas:
            result["fora_padrao"].append({
                "arquivo": str(p),
                "problemas": problemas,
            })

    # 3. grupos sobrepostos (candidatas a merge) via overlap de keywords (título+tags)
    kw_by_file = {}
    for p, fm, body, text in notas_atomicas:
        title = p.stem
        tags_str = fm.get("tags", "")
        kw_by_file[str(p)] = keywords(title, tags_str)

    files_list = list(kw_by_file.items())
    seen_pairs = set()
    grupos = []
    for i in range(len(files_list)):
        f1, kw1 = files_list[i]
        if not kw1:
            continue
        for j in range(i + 1, len(files_list)):
            f2, kw2 = files_list[j]
            if not kw2:
                continue
            inter = kw1 & kw2
            union = kw1 | kw2
            if not union:
                continue
            jaccard = len(inter) / len(union)
            if jaccard >= 0.4 and len(inter) >= 2:
                grupos.append({
                    "arquivos": [f1, f2],
                    "keywords_em_comum": sorted(inter),
                    "similaridade": round(jaccard, 2),
                })
    result["grupos_sobrepostos"] = grupos

    # 4. registros crus com conteúdo técnico substancial e sem nenhuma nota atômica citando-o como Fonte/Origem
    origem_citada = set()
    for p, fm, body, text in notas_atomicas:
        for m in re.finditer(r"Origem:\s*\[\[([^\]]+)\]\]", body):
            origem_citada.add(m.group(1).strip())

    for p, fm, body, text in registros:
        wc = word_count(body)
        if wc < 150:
            continue
        stem = p.stem
        if stem in origem_citada:
            continue
        result["registros_destilaveis"].append({
            "arquivo": str(p),
            "palavras": wc,
        })

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
