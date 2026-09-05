param(
    [string]$Project = (Join-Path $PSScriptRoot '../..'),
    [string]$Image = 'ghcr.io/inti-cmnb/kicad10_auto_full@sha256:dd3b846da945f204fa7b61916df34a99170b2a2095b49c3879cd96d414b8a7b8',
    [switch]$DryRun
)
# Experimental local environment probe. It does not run the output/release workflow.
$ErrorActionPreference = 'Stop'
$reviewProject = (Resolve-Path -LiteralPath $Project).Path
if (-not (Test-Path -LiteralPath $reviewProject -PathType Container)) {throw 'Project must be a directory'}
$reviewArguments = @('run','--rm','--mount',"type=bind,source=$reviewProject,target=/work,readonly",'--workdir','/work','--entrypoint','/bin/bash',$Image,'-lc','kicad-cli --version && kibot --version')
if ($DryRun) {
    [pscustomobject]@{Executable='docker';Arguments=$reviewArguments;Purpose='Read-only KiCad/KiBot version probe, not output generation'} | ConvertTo-Json -Depth 3
    exit 0
}
& docker @reviewArguments
exit $LASTEXITCODE
