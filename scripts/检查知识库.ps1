$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

$files = Get-ChildItem -File -Recurse $root |
  Where-Object { $_.FullName -notmatch '\\.git(\\|$)' }
$markdown = $files | Where-Object Extension -eq '.md'
$broken = @()
$pattern = '\[[^\]]+\]\(([^)]+)\)'

foreach ($file in $markdown) {
  if ($file.FullName -match '\\_research\\') { continue }
  $text = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8
  foreach ($match in [regex]::Matches($text, $pattern)) {
    $link = $match.Groups[1].Value.Trim()
    if ($link -match '^(https?://|mailto:|#)') { continue }
    $pathPart = $link.Split('#')[0].Split('?')[0]
    if ([string]::IsNullOrWhiteSpace($pathPart)) { continue }
    $candidate = Join-Path $file.DirectoryName ($pathPart -replace '/', '\\')
    if (-not (Test-Path -LiteralPath $candidate)) {
      $broken += "$($file.FullName): $link"
    }
  }
}

Write-Output "根目录：$root"
Write-Output "文件总数：$($files.Count)"
Write-Output "Markdown 总数：$($markdown.Count)"
Write-Output "核心 Markdown 断链：$($broken.Count)"
if ($broken.Count -gt 0) {
  $broken | ForEach-Object { Write-Output $_ }
  exit 1
}
