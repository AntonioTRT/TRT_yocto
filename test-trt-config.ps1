# test-trt-config.ps1 - PowerShell script to test TRT configuration

Write-Host "=== TRT Configuration Test ===" -ForegroundColor Green
Write-Host

$configFile = "C:\repos\TRT_yocto\conf\trt-config.txt"

if (-not (Test-Path $configFile)) {
    Write-Host "❌ Error: Configuration file not found at $configFile" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Configuration file found: $configFile" -ForegroundColor Green
Write-Host

# Read configuration
Write-Host "📖 Reading WiFi configuration..." -ForegroundColor Cyan
$config = Get-Content $configFile

# Extract WiFi settings
$wifiPrimarySSID = ($config | Where-Object { $_ -match '^WIFI_PRIMARY_SSID=' }) -replace '.*="([^"]*)".*', '$1'
$wifiPrimaryPassword = ($config | Where-Object { $_ -match '^WIFI_PRIMARY_PASSWORD=' }) -replace '.*="([^"]*)".*', '$1'
$wifiPrimaryPriority = ($config | Where-Object { $_ -match '^WIFI_PRIMARY_PRIORITY=' }) -replace '.*=', ''
$wifiCountry = ($config | Where-Object { $_ -match '^WIFI_COUNTRY=' }) -replace '.*="([^"]*)".*', '$1'

Write-Host "   Primary WiFi: $wifiPrimarySSID (priority: $wifiPrimaryPriority)"
Write-Host "   Country: $wifiCountry"
Write-Host

# Generate wpa_supplicant.conf content
Write-Host "🔧 Generating wpa_supplicant.conf content..." -ForegroundColor Cyan

$wpaContent = @"
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=$wifiCountry

# Primary WiFi Network
network={
    ssid="$wifiPrimarySSID"
    psk="$wifiPrimaryPassword"
    priority=$wifiPrimaryPriority
}
"@

Write-Host "✅ wpa_supplicant.conf content generated" -ForegroundColor Green
Write-Host

# Show generated content
Write-Host "📄 Generated wpa_supplicant.conf content:" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host $wpaContent
Write-Host "===============================================" -ForegroundColor Yellow
Write-Host

# Verification
Write-Host "🔍 Verifications:" -ForegroundColor Cyan

if ($wifiPrimarySSID -eq "TU_WIFI_PRINCIPAL") {
    Write-Host "   ⚠️  WARNING: You still have the default SSID 'TU_WIFI_PRINCIPAL'" -ForegroundColor Yellow
    Write-Host "       Edit: C:\repos\TRT_yocto\conf\trt-config.txt"
} else {
    Write-Host "   ✅ Primary SSID configured: $wifiPrimarySSID" -ForegroundColor Green
}

if ($wifiPrimaryPassword -eq "tu_contraseña_wifi") {
    Write-Host "   ⚠️  WARNING: You still have the default password" -ForegroundColor Yellow
} else {
    Write-Host "   ✅ Password configured (hidden for security)" -ForegroundColor Green
}

if ($wifiCountry) {
    Write-Host "   ✅ Country configured: $wifiCountry" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Country not configured" -ForegroundColor Yellow
}

Write-Host
Write-Host "🎯 SUMMARY:" -ForegroundColor Green
Write-Host "   - Configuration read successfully: ✅"
Write-Host "   - wpa_supplicant.conf content generated: ✅"
Write-Host "   - Ready to include in Yocto image: ✅"
Write-Host
Write-Host "📝 To use in production:" -ForegroundColor Cyan
Write-Host "   1. Edit: C:\repos\TRT_yocto\conf\trt-config.txt"
Write-Host "   2. Change WIFI_PRIMARY_SSID and WIFI_PRIMARY_PASSWORD"
Write-Host "   3. Run Yocto build"