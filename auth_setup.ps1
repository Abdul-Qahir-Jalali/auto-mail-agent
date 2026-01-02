$json = Get-Content "credentials.json" | Out-String | ConvertFrom-Json
$creds = if ($json.installed) { $json.installed } else { $json.web }

$env:GMAIL_CLIENT_ID = $creds.client_id
$env:GMAIL_CLIENT_SECRET = $creds.client_secret
$env:GMAIL_REDIRECT_URI = $creds.redirect_uris[0]

Write-Host "Starting Authentication for Client ID: $($env:GMAIL_CLIENT_ID)"
Write-Host "A browser window should open, or a URL will follow."
Write-Host "Please complete the login."

npx gmail-mcp-server
