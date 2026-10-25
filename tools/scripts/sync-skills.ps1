[CmdletBinding(SupportsShouldProcess = $true, ConfirmImpact = "Medium")]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Assert-NoReparsePoints {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,

        [Parameter(Mandatory = $true)]
        [string]$Context
    )

    $rootItem = Get-Item -LiteralPath $Path -Force
    if (($rootItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw "$Context contains a symbolic link or reparse point: $($rootItem.FullName)"
    }

    $pendingDirectories = [System.Collections.Generic.Stack[string]]::new()
    $pendingDirectories.Push($rootItem.FullName)
    while ($pendingDirectories.Count -gt 0) {
        $currentDirectory = $pendingDirectories.Pop()
        foreach ($item in (Get-ChildItem -LiteralPath $currentDirectory -Force)) {
            if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "$Context contains a symbolic link or reparse point: $($item.FullName)"
            }
            if ($item.PSIsContainer) {
                $pendingDirectories.Push($item.FullName)
            }
        }
    }
}

function Get-TreeFingerprint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        return $null
    }

    $root = [System.IO.Path]::GetFullPath($Path).TrimEnd('\', '/')
    $entries = foreach ($item in (Get-ChildItem -LiteralPath $root -Recurse -Force | Sort-Object FullName)) {
        $relative = $item.FullName.Substring($root.Length).TrimStart('\', '/')
        if ($item.PSIsContainer) {
            "D|$relative"
        }
        else {
            $stream = [System.IO.File]::OpenRead($item.FullName)
            try {
                $algorithm = [System.Security.Cryptography.SHA256]::Create()
                try {
                    $hashBytes = $algorithm.ComputeHash($stream)
                }
                finally {
                    $algorithm.Dispose()
                }
            }
            finally {
                $stream.Dispose()
            }
            $hash = [System.BitConverter]::ToString($hashBytes).Replace("-", "")
            "F|$relative|$($item.Length)|$hash"
        }
    }

    return (@($entries) -join "`n")
}

function Get-MetadataValue {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Metadata,

        [Parameter(Mandatory = $true)]
        [string]$Field,

        [Parameter(Mandatory = $true)]
        [string]$SkillName
    )

    $pattern = '(?m)^' + [regex]::Escape($Field) + ':[ \t]*(?<value>[^\r\n]+?)[ \t]*\r?$'
    $matches = [regex]::Matches($Metadata, $pattern)
    if ($matches.Count -ne 1) {
        throw "Invalid skill '$SkillName': metadata '$Field' must appear exactly once."
    }

    $value = $matches[0].Groups["value"].Value.Trim()
    if ($value.Length -ge 2) {
        $first = $value[0]
        $last = $value[$value.Length - 1]
        if (($first -eq '"' -and $last -eq '"') -or ($first -eq "'" -and $last -eq "'")) {
            $value = $value.Substring(1, $value.Length - 2).Trim()
        }
    }
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Invalid skill '$SkillName': metadata '$Field' cannot be empty."
    }

    return $value
}

function Get-ValidatedSkills {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SourceRoot
    )

    if (-not (Test-Path -LiteralPath $SourceRoot -PathType Container)) {
        throw "Canonical skills directory not found: $SourceRoot"
    }

    Assert-NoReparsePoints -Path $SourceRoot -Context "Canonical skills directory"

    $directories = @(Get-ChildItem -LiteralPath $SourceRoot -Directory -Force | Sort-Object Name)
    if ($directories.Count -eq 0) {
        throw "No skill directories found in: $SourceRoot"
    }

    $validated = foreach ($directory in $directories) {
        if ($directory.Name -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
            throw "Invalid skill directory '$($directory.Name)': use lowercase kebab-case."
        }

        Assert-NoReparsePoints -Path $directory.FullName -Context "Skill '$($directory.Name)'"

        $skillFile = Join-Path $directory.FullName "SKILL.md"
        if (-not (Test-Path -LiteralPath $skillFile -PathType Leaf)) {
            throw "Invalid skill '$($directory.Name)': SKILL.md was not found."
        }

        $content = Get-Content -LiteralPath $skillFile -Raw -Encoding utf8
        $content = $content.TrimStart([char]0xFEFF)
        $frontMatter = [regex]::Match(
            $content,
            '\A---\r?\n(?<metadata>.*?)\r?\n---(?:\r?\n|\z)',
            [System.Text.RegularExpressions.RegexOptions]::Singleline
        )
        if (-not $frontMatter.Success) {
            throw "Invalid skill '$($directory.Name)': SKILL.md must start with YAML frontmatter."
        }

        $metadata = $frontMatter.Groups["metadata"].Value
        $name = Get-MetadataValue -Metadata $metadata -Field "name" -SkillName $directory.Name
        [void](Get-MetadataValue -Metadata $metadata -Field "description" -SkillName $directory.Name)

        if ($name -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
            throw "Invalid skill '$($directory.Name)': metadata 'name' must use lowercase kebab-case."
        }
        if ($name -cne $directory.Name) {
            throw "Invalid skill '$($directory.Name)': metadata name '$name' does not match the directory."
        }

        Write-Host "[valid] $($directory.Name)"
        [PSCustomObject]@{
            Name        = $directory.Name
            SourcePath  = $directory.FullName
            Fingerprint = Get-TreeFingerprint -Path $directory.FullName
        }
    }

    return @($validated)
}

function Assert-GeneratedDestination {
    param(
        [Parameter(Mandatory = $true)]
        [string]$DestinationRoot
    )

    if (-not (Test-Path -LiteralPath $DestinationRoot)) {
        return
    }
    if (-not (Test-Path -LiteralPath $DestinationRoot -PathType Container)) {
        throw "Generated destination is not a directory: $DestinationRoot"
    }

    Assert-NoReparsePoints -Path $DestinationRoot -Context "Generated destination"

    foreach ($item in (Get-ChildItem -LiteralPath $DestinationRoot -Force)) {
        if (-not $item.PSIsContainer) {
            throw "Generated destination contains an unmanaged file: $($item.FullName)"
        }
        Assert-NoReparsePoints -Path $item.FullName -Context "Generated skill '$($item.Name)'"
        if (-not (Test-Path -LiteralPath (Join-Path $item.FullName "SKILL.md") -PathType Leaf)) {
            throw "Generated destination contains an unmanaged directory: $($item.FullName)"
        }
    }
}

try {
    $repositoryRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
    $sourceRoot = [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot "skills"))
    $destinationRoots = @(
        [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot ".claude\skills")),
        [System.IO.Path]::GetFullPath((Join-Path $repositoryRoot ".agents\skills"))
    )

    $repositoryPrefix = $repositoryRoot.TrimEnd('\', '/') + [System.IO.Path]::DirectorySeparatorChar
    foreach ($destinationRoot in $destinationRoots) {
        if ($destinationRoot -eq $sourceRoot -or -not $destinationRoot.StartsWith($repositoryPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Unsafe generated destination: $destinationRoot"
        }
    }

    Write-Host "Validating canonical skills in: $sourceRoot"
    $skills = @(Get-ValidatedSkills -SourceRoot $sourceRoot)
    Write-Host "Validation completed: $($skills.Count) skill(s)."

    foreach ($destinationRoot in $destinationRoots) {
        Assert-GeneratedDestination -DestinationRoot $destinationRoot
    }

    $totalCreated = 0
    $totalUpdated = 0
    $totalUnchanged = 0
    $totalRemoved = 0
    $appliedDestinations = 0

    foreach ($destinationRoot in $destinationRoots) {
        $existing = @()
        if (Test-Path -LiteralPath $destinationRoot -PathType Container) {
            $existing = @(Get-ChildItem -LiteralPath $destinationRoot -Directory -Force)
        }

        $sourceNames = @($skills.Name)
        $stale = @($existing | Where-Object { $_.Name -notin $sourceNames })
        $created = @()
        $updated = @()
        $unchanged = @()

        foreach ($skill in $skills) {
            $target = Join-Path $destinationRoot $skill.Name
            if (-not (Test-Path -LiteralPath $target -PathType Container)) {
                $created += $skill
            }
            elseif ((Get-TreeFingerprint -Path $target) -ceq $skill.Fingerprint) {
                $unchanged += $skill
            }
            else {
                $updated += $skill
            }
        }

        $totalCreated += $created.Count
        $totalUpdated += $updated.Count
        $totalUnchanged += $unchanged.Count
        $totalRemoved += $stale.Count
        $action = "create $($created.Count), update $($updated.Count), keep $($unchanged.Count), remove $($stale.Count)"

        if (-not $PSCmdlet.ShouldProcess($destinationRoot, "Synchronize generated skills ($action)")) {
            Write-Host "[plan] $destinationRoot - $action"
            continue
        }

        if (-not (Test-Path -LiteralPath $destinationRoot -PathType Container)) {
            New-Item -ItemType Directory -Path $destinationRoot -Force | Out-Null
        }

        foreach ($directory in $stale) {
            Remove-Item -LiteralPath $directory.FullName -Recurse -Force
            Write-Host "[removed] $($directory.FullName)"
        }

        foreach ($skill in $created) {
            Copy-Item -LiteralPath $skill.SourcePath -Destination $destinationRoot -Recurse -Force
            Write-Host "[created] $(Join-Path $destinationRoot $skill.Name)"
        }

        foreach ($skill in $updated) {
            $target = Join-Path $destinationRoot $skill.Name
            Remove-Item -LiteralPath $target -Recurse -Force
            Copy-Item -LiteralPath $skill.SourcePath -Destination $destinationRoot -Recurse -Force
            Write-Host "[updated] $target"
        }

        foreach ($skill in $unchanged) {
            Write-Host "[unchanged] $(Join-Path $destinationRoot $skill.Name)"
        }

        $appliedDestinations++
    }

    $mode = if ($appliedDestinations -eq $destinationRoots.Count) { "completed" } else { "planned" }
    Write-Host "Synchronization ${mode}: created $totalCreated, updated $totalUpdated, unchanged $totalUnchanged, removed $totalRemoved."
    Write-Host "Canonical source was not modified: $sourceRoot"
}
catch {
    Write-Error "Skill synchronization failed: $($_.Exception.Message)"
    exit 1
}
