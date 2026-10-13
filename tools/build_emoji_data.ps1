# Build emoji data using PowerShell from downloaded CLDR and emoji-test files

$baseFile = "C:\Users\rexya\.gemini\antigravity\brain\bbb678a2-d75e-423b-bd3c-c0154eac08a1\.system_generated\steps\77\content.md"
$derivedFile = "C:\Users\rexya\.gemini\antigravity\brain\bbb678a2-d75e-423b-bd3c-c0154eac08a1\.system_generated\steps\81\content.md"
$testFile = "C:\Users\rexya\.gemini\antigravity\brain\bbb678a2-d75e-423b-bd3c-c0154eac08a1\.system_generated\steps\86\content.md"
$overridesFile = "c:\Emoji-ID\tools\overrides.tsv"
$outFile = "c:\Emoji-ID\addon\globalPlugins\emojiID\data\emoji_id.json"

function Clean-Markdown-Json($filePath) {
    $lines = Get-Content $filePath -Encoding utf8
    $jsonStartIndex = -1
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i].Trim() -eq '{') {
            $jsonStartIndex = $i
            break
        }
    }
    if ($jsonStartIndex -ge 0) {
        $jsonText = ($lines[$jsonStartIndex..($lines.Length - 1)]) -join "`n"
        return $jsonText | ConvertFrom-Json
    }
    throw "No JSON found in $filePath"
}

function Normalize-Emoji($str) {
    return $str -replace "[\uFE0E\uFE0F]", ""
}

Write-Host "Parsing Base Annotations..."
$baseObj = Clean-Markdown-Json $baseFile
$baseMap = @{}
$baseAnn = $baseObj.annotations.annotations
foreach ($prop in $baseAnn.PSObject.Properties) {
    $emoji = $prop.Name
    $val = $prop.Value
    if ($val.tts -and $val.tts.Count -gt 0) {
        $norm = Normalize-Emoji $emoji
        $baseMap[$norm] = $val.tts[0]
    }
}
Write-Host "Base annotations count: $($baseMap.Count)"

Write-Host "Parsing Derived Annotations..."
$derivedObj = Clean-Markdown-Json $derivedFile
$derivedMap = @{}
$derivedAnn = $derivedObj.annotationsDerived.annotations
foreach ($prop in $derivedAnn.PSObject.Properties) {
    $emoji = $prop.Name
    $val = $prop.Value
    if ($val.tts -and $val.tts.Count -gt 0) {
        $norm = Normalize-Emoji $emoji
        $derivedMap[$norm] = $val.tts[0]
    }
}
Write-Host "Derived annotations count: $($derivedMap.Count)"

# Merge: Base then Derived
$merged = @{}
foreach ($k in $baseMap.Keys) { $merged[$k] = $baseMap[$k] }
foreach ($k in $derivedMap.Keys) { $merged[$k] = $derivedMap[$k] }

Write-Host "Loading Overrides..."
$overrideCount = 0
if (Test-Path $overridesFile) {
    $lines = Get-Content $overridesFile -Encoding utf8
    foreach ($line in $lines) {
        $trim = $line.Trim()
        if (-not $trim -or $trim.StartsWith("#")) { continue }
        $parts = $trim -split "`t"
        if ($parts.Length -ge 2) {
            $emoji = Normalize-Emoji ($parts[0].Trim())
            $name = $parts[1].Trim()
            if ($emoji -and $name) {
                Write-Host "  Override: $emoji -> $name"
                $merged[$emoji] = $name
                $overrideCount++
            }
        }
    }
}
Write-Host "Overrides applied: $overrideCount"
Write-Host "Total unique entries: $($merged.Count)"

# Coverage check against emoji-test.txt
Write-Host "Analyzing Coverage against emoji-test.txt..."
$testLines = Get-Content $testFile -Encoding utf8
$fullyQualified = [System.Collections.Generic.List[string]]::new()
foreach ($line in $testLines) {
    $trim = $line.Trim()
    if (-not $trim -or $trim.StartsWith("#")) { continue }
    if ($trim -like "*; fully-qualified*") {
        $cpPart = ($trim -split ";")[0].Trim()
        $hexCodes = $cpPart -split "\s+"
        $chars = [System.Collections.Generic.List[string]]::new()
        foreach ($h in $hexCodes) {
            $code = [Convert]::ToInt32($h, 16)
            $chars.Add([char]::ConvertFromUtf32($code))
        }
        $fullyQualified.Add(($chars -join ""))
    }
}
Write-Host "Total fully-qualified emojis: $($fullyQualified.Count)"

$covered = 0
$missingList = [System.Collections.Generic.List[string]]::new()
foreach ($fq in $fullyQualified) {
    $norm = Normalize-Emoji $fq
    if ($merged.ContainsKey($norm)) {
        $covered++
    } else {
        $missingList.Add($fq)
    }
}

$pct = [math]::Round(($covered / $fullyQualified.Count) * 100, 1)
Write-Host "Covered: $covered / $($fullyQualified.Count) ($pct%)"
Write-Host "Missing: $($missingList.Count)"

# Sort by key length descending, then key for determinism
$sortedKeys = $merged.Keys | Sort-Object -Property @{Expression={$_.Length}; Descending=$true}, @{Expression={$_}; Descending=$false}

$orderedData = [ordered]@{}
foreach ($k in $sortedKeys) {
    $orderedData[$k] = $merged[$k]
}

$outputObj = [ordered]@{
    version = "48.2.0"
    emoji_version = "16.0"
    count = $orderedData.Count
    covered_fully_qualified = $covered
    total_fully_qualified = $fullyQualified.Count
    coverage_percent = $pct
    license = "UNICODE LICENSE V3 - Copyright (c) 1991-2026 Unicode, Inc. Data from CLDR 48.2.0. See https://www.unicode.org/license for full license text."
    data = $orderedData
}

$targetDir = Split-Path $outFile -Parent
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$jsonOutput = $outputObj | ConvertTo-Json -Depth 5 -Compress
[System.IO.File]::WriteAllText($outFile, $jsonOutput, [System.Text.Encoding]::UTF8)

$size = (Get-Item $outFile).Length
Write-Host "Output written to: $outFile ($size bytes)"

# Write missing sample report
$missingReportFile = "c:\Emoji-ID\tools\missing_emoji_report.txt"
$reportLines = [System.Collections.Generic.List[string]]::new()
$reportLines.Add("Emoji ID - Coverage Report vs Unicode 16.0 emoji-test.txt")
$reportLines.Add("CLDR Version: 48.2.0")
$reportLines.Add("Fully-qualified emoji: $($fullyQualified.Count)")
$reportLines.Add("Covered in Indonesian CLDR: $covered ($pct%)")
$reportLines.Add("Missing count: $($missingList.Count)")
$reportLines.Add("")
$reportLines.Add("Missing Emojis:")
foreach ($m in $missingList) {
    $cps = ($m.EnumerateRunes() | ForEach-Object { "U+{0:X4}" -f $_.Value }) -join " "
    $reportLines.Add("  $m ($cps)")
}
[System.IO.File]::WriteAllLines($missingReportFile, $reportLines, [System.Text.Encoding]::UTF8)
Write-Host "Missing emoji report written to $missingReportFile"
