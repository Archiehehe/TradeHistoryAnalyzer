param(
  [string]$BaseUrl = 'http://127.0.0.1:8000'
)

$response = Invoke-RestMethod -Uri "$BaseUrl/api/integrations/status"
$response | ConvertTo-Json -Depth 8
