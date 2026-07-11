. "$PSScriptRoot\_common.ps1"

Enter-BackendRoot
$python = Get-BackendPython
& $python -m pytest tests
