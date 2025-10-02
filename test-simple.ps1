# test-trt-config-simple.ps1 - Simple PowerShell script to test TRT configuration

Write-Host "=== TRT Configuration Test ===" -ForegroundColor Green
Write-Host

$configFile = "C:\repos\TRT_yocto\conf\trt-config.txt"

if (-not (Test-Path $configFile)) {
    Write-Host "Error: Configuration file not found at $configFile" -ForegroundColor Red
    exit 1
}

Write-Host "Configuration file found: $configFile" -ForegroundColor Green
Write-Host

# Read and display configuration
Write-Host "Reading WiFi configuration..." -ForegroundColor Cyan
$content = Get-Content $configFile

Write-Host "Current WiFi settings:" -ForegroundColor Yellow
$content | Where-Object { $_ -match "WIFI_PRIMARY" } | ForEach-Object {
    Write-Host "  $_"
}

Write-Host
Write-Host "Current country setting:" -ForegroundColor Yellow
$content | Where-Object { $_ -match "WIFI_COUNTRY" } | ForEach-Object {
    Write-Host "  $_"
}

Write-Host
Write-Host "Configuration file content preview:" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
$content | Select-Object -First 15 | ForEach-Object {
    Write-Host $_
}
Write-Host "====================================" -ForegroundColor Cyan

Write-Host
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. Edit the file: $configFile"
Write-Host "2. Change WIFI_PRIMARY_SSID to your WiFi name"
Write-Host "3. Change WIFI_PRIMARY_PASSWORD to your WiFi password"
Write-Host "4. Run Yocto build to create image with your WiFi settings"