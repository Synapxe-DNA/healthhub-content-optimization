#!/bin/bash

# Perform operations in the root directory using a subshell
(
    # Navigate to the root of the project
    cd "$(git rev-parse --show-toplevel)" || exit

    # Define the config file path relative to the root
    CONFIG_FILE_PATH=".dvc/config.local"

    # Attempt to remove the config file
    if [ -f "$CONFIG_FILE_PATH" ]; then
        echo "Removing config.local."
        rm "$CONFIG_FILE_PATH"
    else
        echo "config.local not found, continuing."
    fi
)

# Path to the .env file
ENV_FILE=".env"

# Check if the .env file exists and add a newline if it's missing
if [ -f "$ENV_FILE" ]; then
    [ -n "$(tail -c1 "$ENV_FILE")" ] && echo >> "$ENV_FILE"
else
    echo "Error: $ENV_FILE file not found!"
    exit 1
fi

# Read through the .env file and export each variable
while IFS='=' read -r key value; do
    # Ignore empty lines and comments
    if [[ -z "$key" || "$key" == \#* ]]; then
        continue
    fi

    # Trim any surrounding whitespace (useful for some environments)
    key=$(echo "$key" | xargs)
    value=$(echo "$value" | xargs)

    # Export the variable
    export "$key"="$value"

done < "$ENV_FILE"

echo "Environment variables set."

# Define your remote names in an array
remotes=("all_contents" "missing_contents" "google_analytics" "ground_truth")

# Loop through each remote and execute the DVC commands
for remote in "${remotes[@]}"; do
    # Add remote with base URL
    dvc remote add "$remote" "$AZURE_URL/$remote" --force

    # Add local configurations for credentials
    dvc remote modify --local "$remote" account_name "$AZURE_STORAGE_ACCOUNT"
    dvc remote modify --local "$remote" sas_token "$AZURE_STORAGE_SAS_TOKEN"

done

# Inform the user of completion
echo "All remotes have been configured."
