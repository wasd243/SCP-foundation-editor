param([string]$pattern = "v3.0.0-alpha.*")

$tags = git ls-remote --tags origin | ForEach-Object {
    ($_ -split "refs/tags/")[1] -replace '\^\{\}$', ''
} | Where-Object { $_ -like $pattern }

if ($tags.Count -eq 0) {
    Write-Host "no tags"
    return
}

Write-Host "Will delete $($tags.Count) tag(s)："
$tags | ForEach-Object { Write-Host "  - $_" }

$confirm = Read-Host "Are you sure?(y/N)"
if ($confirm -eq "y") {
    $tags | ForEach-Object { git push origin --delete $_ }
} else {
    Write-Host "Canceled."
}
