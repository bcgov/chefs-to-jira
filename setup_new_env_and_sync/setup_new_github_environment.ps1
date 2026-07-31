# Setup a new GitHub environment by pushing secrets and variables from newEnvironmentConfig.json.
#
# Usage:
#   # Generate newEnvironmentConfig.json from environmentTemplate.example.json:
#   .\setup_new_github_environment.ps1 -GenerateConfig
#
#   # Push secrets and variables to the GitHub environment recorded in newEnvironmentConfig.json:
#   .\setup_new_github_environment.ps1 -GenerateEnvironment
#
# The list of secret and variable names is driven by environmentTemplate.example.json,
# so add or remove entries there to change what gets synced.
#
# -GenerateConfig writes newEnvironmentConfig.json using the example file's values
# as defaults, and prompts for the GitHub environment name. Review and obfuscate
# secrets before committing that file.
#
# -GenerateEnvironment reads newEnvironmentConfig.json and pushes its secrets and
# variables to the GitHub environment named in that file.
#
# Requires: gh CLI authenticated, git remote configured.

param(
  [switch]$GenerateConfig,
  [switch]$GenerateEnvironment
)

$ErrorActionPreference = "Stop"

$scriptDir = $PSScriptRoot
$exampleFile = Join-Path $scriptDir "environmentTemplate.example.json"
$configFile = Join-Path $scriptDir "newEnvironmentConfig.json"
$repoRoot = Split-Path -Parent $scriptDir

if (-not $GenerateConfig -and -not $GenerateEnvironment) {
  Write-Error "Specify -GenerateConfig to create newEnvironmentConfig.json, or -GenerateEnvironment to push to GitHub."
  exit 1
}

if ($GenerateConfig -and $GenerateEnvironment) {
  Write-Error "Specify only one of -GenerateConfig or -GenerateEnvironment, not both."
  exit 1
}

if (-not (Test-Path $exampleFile)) {
  Write-Error "environmentTemplate.example.json not found at $exampleFile"
  exit 1
}

$exampleContent = Get-Content $exampleFile -Raw
$example = $exampleContent | ConvertFrom-Json

# Derive the authoritative list of secret and variable names from the example JSON,
# preserving the key order from the source file.
$secretNames = @()
$variableNames = @()

$exampleLines = Get-Content $exampleFile
$inSection = $null
foreach ($line in $exampleLines) {
  if ($line -match '"secrets"\s*:\s*\{') {
    $inSection = "secrets"
    continue
  }
  if ($line -match '"variables"\s*:\s*\{') {
    $inSection = "variables"
    continue
  }
  if ($inSection -and $line -match '^\s*\}') {
    $inSection = $null
    continue
  }
  if ($inSection -and $line -match '"([^"]+)"\s*:') {
    if ($inSection -eq "secrets") {
      $secretNames += $Matches[1]
    }
    elseif ($inSection -eq "variables") {
      $variableNames += $Matches[1]
    }
  }
}

# --- Generate newEnvironmentConfig.json from the example file ---
if ($GenerateConfig) {
  $environmentName = Read-Host "Enter the GitHub environment name"
  if ([string]::IsNullOrWhiteSpace($environmentName)) {
    Write-Error "Environment name is required."
    exit 1
  }

  $secretsObj = [ordered]@{}
  foreach ($name in $secretNames) {
    $secretsObj[$name] = $example.secrets.$name
  }

  $variablesObj = [ordered]@{}
  foreach ($name in $variableNames) {
    $variablesObj[$name] = $example.variables.$name
  }

  $config = [ordered]@{
    secrets         = $secretsObj
    variables       = $variablesObj
    environmentName = $environmentName
  } | ConvertTo-Json -Depth 5

  Set-Content -Path $configFile -Value $config -Encoding UTF8
  Write-Host "Config generated at: $configFile"
  Write-Host "Review and obfuscate secrets before using."
}

# --- Push secrets and variables from newEnvironmentConfig.json to a GitHub environment ---
if ($GenerateEnvironment) {
  if (-not (Test-Path $configFile)) {
    Write-Error "newEnvironmentConfig.json not found at $configFile. Run with -GenerateConfig first."
    exit 1
  }

  $configContent = Get-Content $configFile -Raw
  $config = $configContent | ConvertFrom-Json

  if (-not $config.environmentName) {
    Write-Error "environmentName is missing from $configFile."
    exit 1
  }

  $EnvironmentName = $config.environmentName

  $repo = git remote get-url origin
  if ($repo -match 'github\.com[:/]([^/]+)/([^/.]+)') {
    $owner = $Matches[1]
    $repoName = $Matches[2]
  }
  else {
    Write-Error "Could not parse GitHub owner/repo from remote: $repo"
    exit 1
  }

  Write-Host "Creating environment: $EnvironmentName"
  gh api repos/$owner/$repoName/environments/$EnvironmentName -X PUT 2>&1
  if ($LASTEXITCODE -ne 0) {
    Write-Host "Note: Environment may already exist or could not be created. Continuing..."
  }

  Write-Host ""
  Write-Host "Creating workflow file: sync-$EnvironmentName.yml"
  $workflowSource = Join-Path $repoRoot ".github\workflows\sync.yml"
  $workflowDest = Join-Path $repoRoot ".github\workflows\sync-$EnvironmentName.yml"
  if (-not (Test-Path $workflowSource)) {
    Write-Error "Source workflow not found at $workflowSource"
    exit 1
  }
  $workflowContent = Get-Content $workflowSource -Raw
  $workflowContent = $workflowContent -replace 'environment:\s*main', "environment: $EnvironmentName"
  Set-Content -Path $workflowDest -Value $workflowContent -Encoding UTF8
  Write-Host "Workflow created at: $workflowDest"
  foreach ($name in $secretNames) {
    if ($config.secrets.PSObject.Properties[$name]) {
      $value = $config.secrets.$name
      Write-Host "  Secret: $name"
      $value | gh secret set $name --env $EnvironmentName
      if ($LASTEXITCODE -ne 0) {
        Write-Host "    FAILED to set secret: $name"
      }
    }
    else {
      Write-Host "  Secret: $name (not found in config, skipping)"
    }
  }

  Write-Host ""
  Write-Host "Setting variables..."
  foreach ($name in $variableNames) {
    if ($config.variables.PSObject.Properties[$name]) {
      $value = $config.variables.$name
      Write-Host "  Variable: $name"
      gh variable set $name --env $EnvironmentName --body $value
      if ($LASTEXITCODE -ne 0) {
        Write-Host "    FAILED to set variable: $name"
      }
    }
    else {
      Write-Host "  Variable: $name (not found in config, skipping)"
    }
  }

  Write-Host ""
  Write-Host "Done."
}
