param(
  [ValidateSet('upgrade', 'downgrade', 'current', 'history')]
  [string]$Command = 'upgrade',
  [string]$Revision = 'head'
)

. "$PSScriptRoot\_common.ps1"

Enter-BackendRoot
$python = Get-BackendPython

switch ($Command) {
  'upgrade' { & $python -m alembic upgrade $Revision }
  'downgrade' { & $python -m alembic downgrade $Revision }
  'current' { & $python -m alembic current }
  'history' { & $python -m alembic history }
}
