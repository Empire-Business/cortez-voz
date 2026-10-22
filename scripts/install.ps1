$ErrorActionPreference = "Stop"
& python (Join-Path $PSScriptRoot "../cortez/install.py") --apply
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
