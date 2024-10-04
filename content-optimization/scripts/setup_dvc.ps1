# Path to the .env file
$envFile = ".env"

# Check if the .env file exists and add a newline if it's missing
if (Test-Path $envFile) {
    $content = Get-Content $envFile -Raw
    if (-not $content.EndsWith("`n")) {
        Add-Content -Path $envFile -Value "`n"
    }
} else {
    Write-Host "Error: $envFile file not found!"
    exit 1
}

# Read through the .env file and export each variable
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()

    # Ignore empty lines and comments
    if ($line -eq "" -or $line.StartsWith("#")) {
        return
    }

    # Split the line into key and value
    $parts = $line -split '='
    # Trim any surrounding whitespace (useful for some environments)
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()

    # Export the variable to the current session
    [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process)
}

Write-Host "Environment variables set."

# Define your remote names in an array
$remotes = @("all_contents", "missing_contents", "google_analytics")

# Loop through each remote and execute the DVC commands
foreach ($remote in $remotes) {
    # Add remote with base URL
    dvc remote add $remote "$env:GDRIVE_URL/$remote" --force
    dvc remote modify $remote gdrive_acknowledge_abuse true

    # Add local configurations for credentials
    dvc remote modify --local $remote gdrive_client_id $env:GDRIVE_CLIENT_ID
    dvc remote modify --local $remote gdrive_client_secret $env:GDRIVE_CLIENT_SECRET
}

# Inform the user of completion
Write-Host "All remotes have been configured."
