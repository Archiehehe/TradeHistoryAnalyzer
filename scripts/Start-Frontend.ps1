param(
  [string]$Host = '127.0.0.1',
  [int]$Port = 5173,
  [string]$ApiBaseUrl = 'http://127.0.0.1:8000/api'
)

. "$PSScriptRoot\_common.ps1"

Enter-FrontendRoot
if (-not $env:PUBLIC_API_BASE_URL) {
  $env:PUBLIC_API_BASE_URL = $ApiBaseUrl
}

& npm.cmd run dev -- --host $Host --port $Port
