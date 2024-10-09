# Define arrays for file paths and their corresponding remotes
$filePaths = @("data/01_raw/all_contents.dvc", "data/01_raw/missing_contents.dvc", "data/01_raw/google_analytics.xlsx.dvc","data/01_raw/ground_truth.xlsx.dvc")
$remotes = @("all_contents", "missing_contents", "google_analytics", "ground_truth")

# Loop through each file and remote using their indices
for ($i = 0; $i -lt $filePaths.Length; $i++) {
    $filePath = $filePaths[$i]
    $remote = $remotes[$i]
    Write-Host "Pulling $filePath from remote $remote..."
    & dvc pull $filePath --remote $remote
}
