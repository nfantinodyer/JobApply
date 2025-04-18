#Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
[CmdletBinding()]
param (
    [string]$ChromeDir="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    #[string]$ChromeDir="C:\Program Files\Google\Chrome\Application\chrome.exe"
)

#Hard coded 32-bit and 64-bit Chrome paths
$chrome32 = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
$chrome64 = "C:\Program Files\Google\Chrome\Application\chrome.exe"

#if 32-bit Chrome path exists, use that:
if (Test-Path $chrome32) {
    $ChromeDir = $chrome32
}
#if 64-bit path exists, use that:
elseif (Test-Path $chrome64) {
    $ChromeDir = $chrome64
}

if (-Not (Test-Path $ChromeDir -PathType Leaf)) {
    Write-Output "Chrome not found at '$ChromeDir'. Install Chrome or specify a custom location with -ChromeDir."
    Exit 1
}

Write-Host "Using Chrome path: $ChromeDir"

[string]$thisScriptRoot = Join-Path $env:UserProfile "AppData\Local\Programs\Python\Python312"

$chromeDriverRelativeDir = "Scripts"
$chromeDriverDir = $(Join-Path $thisScriptRoot $chromeDriverRelativeDir)
$chromeDriverFileLocation = $(Join-Path $chromeDriverDir "chromedriver.exe")
$chromeVersion = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($ChromeDir).FileVersion
$chromeMajorVersion = $chromeVersion.split(".")[0]

if (-Not (Test-Path $chromeDriverDir -PathType Container)) {
    New-Item -ItemType directory -Path $chromeDriverDir
}

if (Test-Path $chromeDriverFileLocation -PathType Leaf) {
    # get version of curent chromedriver.exe
    $chromeDriverFileVersion = (& $chromeDriverFileLocation --version)
    $chromeDriverFileVersionHasMatch = $chromeDriverFileVersion -match "ChromeDriver (\d+\.\d+\.\d+(\.\d+)?)"
    $chromeDriverCurrentVersion = $matches[1]

if (-Not $chromeDriverFileVersionHasMatch) {
    Exit
}
}
else {
    # if chromedriver.exe not found, will download it
    $chromeDriverCurrentVersion = ''
}

if ($chromeMajorVersion -lt 73) {
    # for chrome versions < 73 will use chromedriver v2.46 (which supports chrome v71-73)
    $chromeDriverExpectedVersion = "2.46"
    $chromeDriverVersionUrl = "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE"
}
else {
    $chromeDriverExpectedVersion = $chromeVersion.split(".")[0..2] -join "."
    $chromeDriverVersionUrl = "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE_" + $chromeDriverExpectedVersion
}

$chromeDriverLatestVersion = Invoke-RestMethod -Uri $chromeDriverVersionUrl

Write-Output "chrome version:       $chromeVersion"
Write-Output "chromedriver version: $chromeDriverCurrentVersion"
Write-Output "chromedriver latest:  $chromeDriverLatestVersion"

# will update chromedriver.exe if MAJOR.MINOR.PATCH
$needUpdateChromeDriver = $chromeDriverCurrentVersion -ne $chromeDriverLatestVersion
if ($needUpdateChromeDriver) {
    $chromeDriverZipLink = "https://storage.googleapis.com/chrome-for-testing-public/" + $chromeDriverLatestVersion + "/win64/chromedriver-win64.zip"
    Write-Output "Will download $chromeDriverZipLink"

    $chromeDriverZipFileLocation = $(Join-Path $chromeDriverDir "chromedriver-win64.zip")

    Invoke-WebRequest -Uri $chromeDriverZipLink -OutFile $chromeDriverZipFileLocation
    Expand-Archive $chromeDriverZipFileLocation -DestinationPath $(Join-Path $thisScriptRoot $chromeDriverRelativeDir) -Force

    if (Test-Path $chromeDriverZipFileLocation -PathType Leaf) {
        Remove-Item -Path $chromeDriverZipFileLocation -Force
    }

    $chromeDriverPath = Join-Path $thisScriptRoot "chromedriver.exe"
    if (Test-Path $chromeDriverPath -PathType Leaf) {
       $chromeDriverFileVersion = & $chromeDriverPath --version
    }

    Move-Item -Path $(Join-Path $thisScriptRoot "Scripts/chromedriver-win64/chromedriver.exe") -Destination $(Join-Path $thisScriptRoot "Scripts") -Force
    Move-Item -Path $(Join-Path $thisScriptRoot "Scripts/chromedriver-win64/LICENSE.chromedriver") -Destination $(Join-Path $thisScriptRoot "Scripts") -Force

    Remove-Item -Path $(Join-Path $thisScriptRoot "Scripts/chromedriver-win64") -Force

    $chromeDriverPath = Join-Path $thisScriptRoot "Scripts/chromedriver.exe"

    Write-Output "chromedriver updated to version $(& $chromeDriverPath --version)"
}
else {
    Write-Output "chromedriver is actual"
}