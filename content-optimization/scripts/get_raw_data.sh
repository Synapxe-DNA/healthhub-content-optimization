#!/bin/bash

# Define parallel arrays for paths and their corresponding remotes
file_paths=("data/01_raw/all_contents.dvc" "data/01_raw/missing_contents.dvc" "data/01_raw/google_analytics.xlsx.dvc", "data/01_raw/ground_truth.xlsx.dvc")
remotes=("all_contents" "missing_contents" "google_analytics", "ground_truth")

# Loop through each file and remote using indexed arrays
for i in "${!file_paths[@]}"; do
    file_path="${file_paths[$i]}"
    remote="${remotes[$i]}"
    echo "Pulling $file_path from remote $remote..."
    dvc pull "$file_path" --remote "$remote"
done
