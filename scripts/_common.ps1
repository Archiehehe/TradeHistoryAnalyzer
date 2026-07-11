$ErrorActionPreference = 'Stop'

function Get-RepoRoot {
  return (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
}

function Get-BackendRoot {
  return (Join-Path (Get-RepoRoot) 'backend')
}

function Get-FrontendRoot {
  return (Join-Path (Get-RepoRoot) 'frontend')
}

function Get-BackendPython {
  $venvPython = Join-Path (Get-BackendRoot) '.venv\Scripts\python.exe'
  if (Test-Path $venvPython) {
    return $venvPython
  }

  $localPython = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
  if (Test-Path $localPython) {
    return $localPython
  }

  $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
  if ($null -ne $pythonCommand) {
    return 'python'
  }

  throw 'No Python interpreter found. Create backend\.venv or install Python 3.12.'
}

function Enter-BackendRoot {
  Set-Location (Get-BackendRoot)
}

function Enter-FrontendRoot {
  Set-Location (Get-FrontendRoot)
}
