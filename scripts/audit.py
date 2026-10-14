#!/usr/bin/env python3
"""Audita a qualidade do catálogo (avisos, não falha o CI).

Complementa validate.py (estrutura): aqui entram as falhas de manutenção que
degradam o acionamento ou deixam o README fora da realidade.
Uso: python3 scripts/audit.py
"""
import glob
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRIGGER = re.compile(r"\b(use|usar|quando|when|trigger|activate|invoke)", re.I)
PAID = re.compile(r"(API[_ ]KEY|OPENROUTER|FAL_KEY|GEMINI_API|GOOGLE_API)", re.I)

readme = open(f"{ROOT}/README.md", encoding="utf8").read()
skills = {}  # "plugin:skill" -> dict
for f in sorted(glob.glob(f"{ROOT}/plugins/*/skills/*/SKILL.md")):
    d = os.path.dirname(f)
    plugin = os.path.basename(os.path.dirname(os.path.dirname(d)))
    name = os.path.basename(d)
    text = open(f, encoding="utf8").read().replace("\r", "")
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    fm, body = m.group(1), m.group(2)
    lines, desc = fm.split("\n"), ""
    for i, l in enumerate(lines):
        if l.startswith("description:"):
            v = l.split(":", 1)[1].strip()
            if v in (">-", ">", "|", "|-"):
                buf, j = [], i + 1
                while j < len(lines) and lines[j].startswith(" "):
                    buf.append(lines[j].strip())
                    j += 1
                v = " ".join(buf)
            desc = v
    skills[f"{plugin}:{name}"] = dict(
        plugin=plugin, name=name, dir=d, fm=fm, body=body, desc=desc,
        lines=len(text.splitlines()),
    )

issues = {}


def warn(key, kind, msg):
    issues.setdefault(kind, []).append(f"{key}: {msg}")


names = {s["name"] for s in skills.values()}
for key, s in skills.items():
    if not TRIGGER.search(s["desc"]):
        warn(key, "description sem gatilho (quando usar)", s["desc"][:60])
    if len(s["desc"]) > 900:
        warn(key, "description perto do limite de 1024", str(len(s["desc"])))
    if s["lines"] > 500 and not os.path.isdir(s["dir"] + "/references"):
        warn(key, "SKILL.md > 500 linhas sem references/", str(s["lines"]))
    if s["plugin"] == "workflow" and "próximo passo" not in s["body"].lower():
        warn(key, "workflow sem 'Próximo passo'", "")
    if PAID.search(s["body"]) and "disable-model-invocation" not in s["fm"]:
        warn(key, "usa API paga sem disable-model-invocation", "")
    if not re.search(rf"`{re.escape(s['name'])}`|`{re.escape(s['name'].split('-')[0])}-\*`", readme):
        warn(key, "ausente do README", "")
    for ref in re.findall(r"`(?:workflow|design|dev|knowledge|marketing|ops):([\w-]+)`", s["body"]):
        if ref not in names:
            warn(key, "referência a skill inexistente", ref)

print(f"{len(skills)} skills auditadas\n")
if not issues:
    print("Nenhuma falha encontrada.")
for kind, items in issues.items():
    print(f"## {kind} ({len(items)})")
    for i in items:
        print(f"- {i}")
    print()
