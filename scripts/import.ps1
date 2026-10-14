<#
.SYNOPSIS
  Importa skills de uma pasta local (padrão: ~/.claude/skills) para um plugin
  deste repositório. Versão Windows/PowerShell do import.sh.

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File scripts\import.ps1 -Plugin <plugin>
  powershell -ExecutionPolicy Bypass -File scripts\import.ps1 -Source C:\caminho\.claude\skills -Plugin <plugin>

.NOTES
  - Só copia pastas que têm SKILL.md.
  - Skill com nome que já existe em outro plugin NÃO entra em plugins/: vai
    para imports/conflicts/<nome>/ para ser comparada e mesclada depois.
  - Para antes de copiar se achar algo com cara de segredo (o repositório é
    público).
#>
param(
  [string]$Source = (Join-Path $HOME ".claude\skills"),
  [Parameter(Mandatory)][string]$Plugin,
  [string[]]$Exclude = @(),
  [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Dest = Join-Path $Root "plugins\$Plugin\skills"
$Conflicts = Join-Path $Root "imports\conflicts"

if (-not (Test-Path (Join-Path $Root "plugins\$Plugin\.claude-plugin\plugin.json"))) {
  throw "Plugin '$Plugin' não existe em plugins\. Use um dos existentes (workflow, knowledge, marketing, design, ops, dev)."
}
if (-not (Test-Path $Source)) { throw "Pasta de origem não encontrada: $Source" }

# Skills que já existem em qualquer plugin do repositório.
$existing = @{}
Get-ChildItem (Join-Path $Root "plugins") -Directory | ForEach-Object {
  $skillsDir = Join-Path $_.FullName "skills"
  if (Test-Path $skillsDir) {
    Get-ChildItem $skillsDir -Directory | ForEach-Object { $existing[$_.Name] = $true }
  }
}

$candidates = if (Test-Path (Join-Path $Source "SKILL.md")) { @(Get-Item $Source) } else { Get-ChildItem $Source -Directory }
$candidates = $candidates | Where-Object { (Test-Path (Join-Path $_.FullName "SKILL.md")) -and ($Exclude -notcontains $_.Name) }
if (-not $candidates) { throw "Nenhuma pasta com SKILL.md em $Source" }

# Varredura de segredos antes de copiar qualquer coisa.
$secretPattern = '(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|(api[_-]?key|secret|password|token)\s*[:=]\s*["'']?[A-Za-z0-9_\-]{16,})'
$hits = foreach ($dir in $candidates) {
  Get-ChildItem $dir.FullName -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -lt 2MB } |
    Select-String -Pattern $secretPattern -ErrorAction SilentlyContinue |
    ForEach-Object { "{0}:{1}" -f $_.Path, $_.LineNumber }
}
if ($hits) {
  Write-Host "Possíveis segredos encontrados (o repositório é público). Nada foi copiado:" -ForegroundColor Red
  $hits | ForEach-Object { Write-Host "  $_" }
  Write-Host "Remova ou troque por variável de ambiente e rode de novo."
  exit 1
}

$imported = 0; $conflicted = 0; $skipped = 0
foreach ($dir in $candidates) {
  $name = $dir.Name
  $target = Join-Path $Dest $name
  if ($existing.ContainsKey($name) -and -not (Test-Path $target)) {
    New-Item -ItemType Directory -Force -Path $Conflicts | Out-Null
    $c = Join-Path $Conflicts $name
    if (Test-Path $c) { Remove-Item $c -Recurse -Force }
    Copy-Item $dir.FullName $c -Recurse
    Write-Host "~ $name já existe em outro plugin -> imports\conflicts\$name (para mesclar)" -ForegroundColor Yellow
    $conflicted++
    continue
  }
  if ((Test-Path $target) -and -not $Force) {
    Write-Host "• $name já existe em $Plugin (use -Force para sobrescrever)"
    $skipped++
    continue
  }
  if (Test-Path $target) { Remove-Item $target -Recurse -Force }
  Copy-Item $dir.FullName $target -Recurse
  Write-Host "+ $name -> plugins\$Plugin\skills\$name" -ForegroundColor Green
  $imported++
}

$gitkeep = Join-Path $Dest ".gitkeep"
if ($imported -gt 0 -and (Test-Path $gitkeep)) { Remove-Item $gitkeep -Force }

Write-Host ""
Write-Host "$imported importada(s), $conflicted em conflito, $skipped já existente(s)."

$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { $py = Get-Command py -ErrorAction SilentlyContinue }
if ($py) { & $py.Source (Join-Path $Root "scripts\validate.py") }
else { Write-Host "Python não encontrado: a validação roda no CI depois do push." }

Write-Host ""
Write-Host "Próximo passo:"
Write-Host "  git add -A"
Write-Host "  git commit -m `"Importa skills pessoais`""
Write-Host "  git push"
