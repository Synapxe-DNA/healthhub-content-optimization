# Perform operations in the root directory using a subshell
& {
    # Navigate to the root of the project
    $rootDir = git rev-parse --show-toplevel
    if (-not $?) { exit }

    # Define the config file path relative to the root
    $configFilePath = Join-Path -Path $rootDir -ChildPath ".dvc/config.local"

    # Attempt to remove the config file
    if (Test-Path -Path $configFilePath) {
        Write-Host "Removing config.local."
        Remove-Item -Path $configFilePath
    } else {
        Write-Host "config.local not found, continuing."
    }
}


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

    # Split the line into key and value, only split on the first occurrence of '='
    $parts = $line -split '=', 2
    # Trim any surrounding whitespace (useful for some environments)
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()

    # Export the variable to the current session
    [System.Environment]::SetEnvironmentVariable($key, $value, [System.EnvironmentVariableTarget]::Process)
}

Write-Host "Environment variables set."

# Define your remote names in an array
$remotes = @("all_contents", "missing_contents", "google_analytics", "ground_truth")

# Loop through each remote and execute the DVC commands
foreach ($remote in $remotes) {
    # Add remote with base URL
    dvc remote add $remote "$env:AZURE_URL/$remote" --force

    # Add local configurations for credentials
    dvc remote modify --local $remote account_name $env:AZURE_STORAGE_ACCOUNT
    dvc remote modify --local $remote sas_token $env:AZURE_STORAGE_SAS_TOKEN
}

# Inform the user of completion
Write-Host "All remotes have been configured."
