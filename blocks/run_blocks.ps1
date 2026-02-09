# Blocks Executor - One-Command Installation and Execution Script (PowerShell)
# This script clones the repository, installs dependencies, executes the workflow, and cleans up
#
# Usage:
#   iwr -useb https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.ps1 | iex
#   Invoke-WebRequest -Uri https://raw.githubusercontent.com/DebalGhosh100/blocks/main/run_blocks.ps1 -OutFile run_blocks.ps1; .\run_blocks.ps1
#   .\run_blocks.ps1 -WorkflowFile "my_workflow.yaml" -ParametersDir "my_parameters"

param(
    [string]$WorkflowFile = "main.yaml",
    [string]$ParametersDir = "parameters"
)

$ErrorActionPreference = "Stop"

# Configuration
$RepoUrl = "https://github.com/DebalGhosh100/blocks.git"
$TempDir = ".blocks_temp"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Blocks Executor - One-Command Execution" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Step 1: Clone repository
Write-Host "[1/5] Cloning repository..." -ForegroundColor Yellow
git clone $RepoUrl $TempDir
Set-Location $TempDir

# Step 2: Install dependencies
Write-Host "[2/5] Installing dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt

# Step 3: Execute workflow
Write-Host "[3/5] Executing workflow..." -ForegroundColor Yellow
Write-Host "Workflow file: $WorkflowFile" -ForegroundColor Gray
Write-Host "Parameters directory: $ParametersDir" -ForegroundColor Gray
python blocks_executor.py "..\$WorkflowFile" --parameters "..\$ParametersDir"

# Step 4: Return to original directory
Write-Host "[4/5] Returning to project directory..." -ForegroundColor Yellow
Set-Location ..

# Step 5: Cleanup
Write-Host "[5/5] Cleaning up framework files..." -ForegroundColor Yellow
Remove-Item -Recurse -Force $TempDir

Write-Host "============================================" -ForegroundColor Green
Write-Host "Execution complete! Framework cleaned up." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
