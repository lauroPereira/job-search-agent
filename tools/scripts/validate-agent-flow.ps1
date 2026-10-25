[CmdletBinding()]
param(
    [string]$ProjectRoot = (Join-Path $PSScriptRoot "..\.."),
    [switch]$SkipGeneratedSkills
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\', '/')
$rootPrefix = $root + [System.IO.Path]::DirectorySeparatorChar
$agentRoot = Join-Path $root "docs\wiki\agents"
$workflowPath = Join-Path $agentRoot "workflow.json"
$flow = Get-Content -LiteralPath $workflowPath -Raw -Encoding utf8 | ConvertFrom-Json
$manifest = Get-Content -LiteralPath (Join-Path $root ".agent-template.json") -Raw -Encoding utf8 | ConvertFrom-Json

function Assert-LocalReference {
    param([string]$Base, [string]$Reference)
    if ([string]::IsNullOrWhiteSpace($Reference) -or [System.IO.Path]::IsPathRooted($Reference)) {
        throw "Expected a relative reference: $Reference"
    }
    $target = [System.IO.Path]::GetFullPath((Join-Path $Base $Reference))
    if (-not $target.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Reference escapes project: $Reference"
    }
    if (-not (Test-Path -LiteralPath $target)) {
        throw "Missing reference: $Reference (from $Base)"
    }
}

function Get-SkillFingerprint {
    param([string]$Directory)
    $entries = foreach ($file in (Get-ChildItem -LiteralPath $Directory -File -Recurse -Force | Sort-Object FullName)) {
        $relative = $file.FullName.Substring($Directory.Length).TrimStart('\', '/')
        $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        "$relative|$hash"
    }
    return (@($entries) -join "`n")
}

if ($flow.kind -ne "declarative" -or $flow.cadence -ne "manual") {
    throw "Workflow must remain declarative and manually invoked."
}
if (@($flow.automatic_external_actions).Count -ne 0) {
    throw "Template workflow cannot authorize automatic external actions."
}
$profiles = @($flow.profiles.PSObject.Properties.Name)
if ($flow.default_profile -notin $profiles) {
    throw "Unknown default profile: $($flow.default_profile)"
}
if ($manifest.update_policy -ne "explicit-review-required") {
    throw "Template updates must remain explicitly reviewed."
}
Assert-LocalReference -Base $agentRoot -Reference $flow.entrypoint
$roles = @($flow.roles.PSObject.Properties.Name)
foreach ($role in $roles) {
    $definition = $flow.roles.$role
    Assert-LocalReference -Base $agentRoot -Reference $definition.prompt
    Assert-LocalReference -Base $agentRoot -Reference $definition.skill
}
foreach ($mode in $flow.lifecycle.PSObject.Properties) {
    Assert-LocalReference -Base $agentRoot -Reference $mode.Value
}
foreach ($kind in @("handoff", "candidate", "story")) {
    Assert-LocalReference -Base $agentRoot -Reference $flow.evidence.$kind
}
$states = @($flow.states)
foreach ($transition in $flow.transitions) {
    if ($transition.from -notin $states -or $transition.to -notin $states) {
        throw "Unknown transition state: $($transition.from) -> $($transition.to)"
    }
    if ($transition.owner -notin ($roles + @("human"))) {
        throw "Unknown transition owner: $($transition.owner)"
    }
    if ([string]::IsNullOrWhiteSpace($transition.condition)) {
        throw "Transition requires an observable condition."
    }
}
Write-Host "[valid] workflow: $($roles.Count) roles, $($states.Count) states, $(@($flow.transitions).Count) transitions"

$documents = @(Get-ChildItem -LiteralPath $agentRoot -Filter "*.md" -File)
$documents += @(Get-Item -LiteralPath (Join-Path $root "docs\templates\passagem-de-papel.md"),
    (Join-Path $root "docs\templates\candidato.md"),
    (Join-Path $root "docs\templates\historia-de-uso.md"))
foreach ($document in $documents) {
    $content = Get-Content -LiteralPath $document.FullName -Raw -Encoding utf8
    # Code examples are data, not paths that must exist.
    $content = [regex]::Replace($content, '(?s)```.*?```', '')
    foreach ($match in [regex]::Matches($content, '\[[^\]]+\]\(([^)]+)\)')) {
        $reference = $match.Groups[1].Value
        if ($reference -match '^(https?://|#)') { continue }
        $reference = ($reference -split '#', 2)[0]
        Assert-LocalReference -Base $document.DirectoryName -Reference $reference
    }
}
Write-Host "[valid] local links and evidence models"

foreach ($path in $manifest.managed_paths) {
    if ($path -notmatch '[*?]') {
        Assert-LocalReference -Base $root -Reference $path
    }
}
Write-Host "[valid] managed paths"

if ($SkipGeneratedSkills) {
    Write-Host "[skipped] generated skills: requested explicitly"
    exit 0
}
$sourceRoot = Join-Path $root "skills"
$sources = @(Get-ChildItem -LiteralPath $sourceRoot -Directory -Force)
$sourceNames = @($sources.Name | Sort-Object)
foreach ($destination in @(".agents\skills", ".claude\skills")) {
    $destinationRoot = Join-Path $root $destination
    $targetNames = @(Get-ChildItem -LiteralPath $destinationRoot -Directory -Force | Select-Object -ExpandProperty Name | Sort-Object)
    if (@(Compare-Object -ReferenceObject $sourceNames -DifferenceObject $targetNames).Count -gt 0) {
        throw "Generated skill inventory differs: $destination"
    }
    foreach ($source in $sources) {
        $target = Join-Path $destinationRoot $source.Name
        if ((Get-SkillFingerprint $source.FullName) -cne (Get-SkillFingerprint $target)) {
            throw "Generated skill differs: $destination/$($source.Name)"
        }
    }
}
Write-Host "[valid] $($sources.Count) canonical skills match both generated destinations"
Write-Host "Agent flow validation completed. This does not prove runtime delegation or external readiness."
