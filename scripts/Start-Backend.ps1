param(
  [string]$Host = '127.0.0.1',
  [int]$Port = 8000
)

. "$PSScriptRoot\_common.ps1"

Enter-BackendRoot
$python = Get-BackendPython
& $python -m uvicorn app.main:app --reload --host $Host --port $Port
