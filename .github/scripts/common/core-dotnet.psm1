#!/usr/bin/env pwsh
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-dotnet.psm1) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Function related to dotnet builds
#
# NOTE: Using this module requires Scripts/Common/Shared-Functions.psm1 to have been loaded first from the DevOps Repo.
#       This should be addressed by https://qontigo-cloud.atlassian.net/browse/DEVXP-902
#

[CmdletBinding(PositionalBinding = $True)]
param(
    [Parameter(Mandatory=$False)]
    [bool]$Debug = $False
)

Set-StrictMode -Version 3.0
$global:ProgressPreference = 'SilentlyContinue'
$suppliedScriptArgs = $PSBoundParameters # $PSBoundParameters inside a function call won't return the params supplied at the command line
if ($True -eq $suppliedScriptArgs['Debug'] -or $DebugPreference -eq 'Continue') {
    $DebugPreference = 'Continue' # We don't want to pause on debug but we do want to see Write-Debug messages
}


function Get-DefaultRuntimeFrameworkVersion {
    <#
    .SYNOPSIS
        Gets the default (current) .NET runtime version installed on the system.

    .OUTPUTS
        The default .NET runtime version.

    .EXAMPLE
        $currentRuntime = Get-DefaultRuntimeFrameworkVersion
        Write-Output "Current .NET runtime version: $currentRuntime"
    #>

    Write-DebugLog "$($MyInvocation.MyCommand.Name)"

    try {
        $dotnetInfo = & dotnet --info 2>&1
    } catch {
        throw [System.InvalidOperationException]::new("dotnet is not installed or not found, cannot determine the runtime version", $_.Exception)
    }

    if (-not $dotnetInfo) {
        throw [System.InvalidOperationException]::new("No .NET runtimes found on the system")
    }

    # The output of `dotnet --info` contains lines like:
    # Host:
    #   Version:      8.0.11
    #
    # So we want to look for Host: followed by Version: on the next line
    $hostVersion = $null
    $inHostSection = $false
    foreach ($line in $dotnetInfo) {
        if ($line -match '^\s*Host:$') {
            $inHostSection = $true
        } elseif ($inHostSection -and $line -match '^\s*Version:\s*(\d+\.\d+\.\d+)$') {
            $hostVersion = $matches[1]
            break
        } elseif ($line -match '^\S') {
            $inHostSection = $false
        }
    }

    if (-not $hostVersion) {
        throw [System.InvalidOperationException]::new("Host version not found in the output of dotnet --info:`n${dotnetInfo}, cannot determine the runtime version")
    }

    return $hostVersion
}


function Get-RuntimeFrameworkVersionForSdk {
    <#
    .SYNOPSIS
        Gets the runtime version for the supplied SDK version from the Microsoft.NETCoreSdk.BundledVersions.props file that comes with every SDK.

    .DESCRIPTION
        This function locates the `Microsoft.NETCoreSdk.BundledVersions.props` file for the supplied SDK version and extracts the value of `BundledNETCoreAppPackageVersion`.

    .PARAMETER SdkVersion
        The SDK version to get the runtime version for.

    .OUTPUTS
        The runtime version for the supplied SDK version or throws an exception if it cannot be determined.

    .EXAMPLE
        $frameworkVersion = Get-RuntimeFrameworkVersionForSdk -SdkVersion "8.0.403" -Debug $True
        $exitCode = $?
        if ($exitCode -ne 0) {
            Write-Error "Failed to get runtime framework version for SDK version: $($frameworkVersion) - exit code $exitCode"
        } else {
            Write-Output "Runtime framework version for SDK version: $frameworkVersion"
        }
    #>
    param (
        [Parameter(Mandatory = $True, Position = 0)]
        [string]$SdkVersion
    )

    Write-DebugLog "$($MyInvocation.MyCommand.Name) -SdkVersion ${SdkVersion}"

    # Check if dotnet is installed
    try {
        $dotnetVersion = dotnet --version 2>&1
        Write-DebugLog "Dotnet Version installed: ${dotnetVersion}"
    }
    catch {
        throw [System.InvalidOperationException]::new("dotnet is not installed or not found, cannot determine the runtime version", $_.Exception)
    }

    # Find the path to the supplied SDK version
    $installedSDKs = & dotnet --list-sdks
    $sdkPath = $installedSDKs | Where-Object { $_ -match "^$SdkVersion " } | ForEach-Object { $_ -split '\s+\[' | Select-Object -Last 1 }
    if (-not $sdkPath) {
        throw [System.InvalidOperationException]::new("SDK version $SdkVersion not found, cannot determine the runtime version.`nInstalled SDKs:`n${installedSDKs}")
    }

    # Remove trailing 'slashes and ']' and construct the SDK version path
    $sdkPath = $sdkPath.TrimEnd("]\/")
    $sdkVersionPath = Join-Path -Path $sdkPath -ChildPath $SdkVersion

    if (-not (Test-Path -Path $sdkVersionPath -PathType Container)) {
        throw [System.IO.DirectoryNotFoundException]::new("SDK version ${SdkVersion}: Path '${sdkVersionPath}' not found, cannot determine the runtime version")
    }

    $propsFile = Join-Path -Path $sdkVersionPath -ChildPath "Microsoft.NETCoreSdk.BundledVersions.props"
    if (-not (Test-Path -Path $propsFile -PathType Leaf)) {
        throw [System.IO.FileNotFoundException]::new("SDK version ${SdkVersion}: Path ${sdkVersionPath} does not contain the required file ${propsFile}, cannot determine the runtime version")
    }

    # Extract the value of BundledNETCoreAppPackageVersion
    [xml]$xml = Get-Content -Path $propsFile
    $bundledNode = $xml.SelectSingleNode("//BundledNETCoreAppPackageVersion")
    if (-not $bundledNode) {
        throw [System.InvalidOperationException]::new("SDK version ${SdkVersion}: Props file at ${propsFile} does not contain a 'BundledNETCoreAppPackageVersion' element, cannot determine the runtime version")
    }
    $runtimeVersion = $bundledNode.InnerText
    if (-not $runtimeVersion) {
        throw [System.InvalidOperationException]::new("SDK version ${SdkVersion}: Props file at ${propsFile} contains a 'BundledNETCoreAppPackageVersion' element without a value, cannot determine the runtime version")

    }

    Write-DebugLog "Runtime version for SDK ${SdkVersion}: $runtimeVersion"

    return $runtimeVersion
}


function Update-RuntimeFrameworkVersion {
    <#
    .SYNOPSIS
        Update the RuntimeFrameworkVersion being set in the supplied Directory.Build.props file with the given value.

    .DESCRIPTION
        Given a Directory.Build.props file, and a framework version, e.g. 8.0.11, this functions finds the target that sets the RuntimeFrameworkVersion with the same major.minor version as that supplied -e.g.

        <Target Name="SetNet8RuntimeFrameworkVersion" Condition="'$(TargetFramework)' == 'net8.0' or '$(TargetFramework)' == 'net8.0-windows'">
            <CreateProperty Value="8.0.10">
                <Output TaskParameter="Value" PropertyName="RuntimeFrameworkVersion" />
            </CreateProperty>
        </Target>

        and replaced the value (8.0.10 in this example) with the supplied value (8.0.11).
        This is typically used to ensure that the runtime version is set correctly for the SDK version being used even if a more recent runtime framework is also installed.

    .PARAMETER FilePath
        The path to the Directory.Build.props file to update.

    .PARAMETER FrameworkVersion
        The runtime framework version to use.

    .EXAMPLE
        Update-RuntimeFrameworkVersion -FilePath "./Directory.Build.props" -FrameworkVersion "8.0.11"
    #>
    param (
        [Parameter(Mandatory = $True, Position = 0, ValueFromPipeline = $True)]
        [string]$FilePath,
        [Parameter(Mandatory = $True, Position = 1)]
        [string]$FrameworkVersion
    )

    Write-DebugLog "$($MyInvocation.MyCommand.Name) -FilePath ${FilePath} -FrameworkVersion ${FrameworkVersion}"

    if ($FrameworkVersion -notmatch '^\d+\.\d+\.\d+$') {
        throw [System.ArgumentException]::new("Invalid Framework Version: '${FrameworkVersion}' - expected format: '<major>.<minor>.<patch>'")
    }

    $defaultVersion = Get-DefaultRuntimeFrameworkVersion
    if (-not (Test-Path $FilePath -PathType Leaf)) {
        $messagePrefix="Props File not found at: '${FilePath}'"
        if ($defaultVersion -eq $FrameworkVersion) {
            Write-InfoLog "${messagePrefix} but the default runtime framework version is already '${FrameworkVersion}' so should be okay"
        }
        else {
            Write-WarningLog "${messagePrefix} and the default runtime framework version (${defaultVersion}) does not match the desired version (${FrameworkVersion}) so you may get unexpected behaviour"
        }
        return
    }

    [xml]$xml = Get-Content $FilePath
    # Find all the <Output TaskParameter="Value" PropertyName="RuntimeFrameworkVersion" /> elements
    $outputElements = $xml.SelectNodes("//Output[@TaskParameter='Value' and @PropertyName='RuntimeFrameworkVersion']")
    if (-not $outputElements) {
        $messagePrefix="No element setting the 'RuntimeFrameworkVersion' was found in the props file at: '${FilePath}'"
        if ($defaultVersion -eq $FrameworkVersion) {
            Write-InfoLog "${messagePrefix} but the default runtime framework version is already '${FrameworkVersion}' so should be okay"
        }
        else {
            Write-WarningLog "${messagePrefix} and the default runtime framework version (${defaultVersion}) does not match the desired version (${FrameworkVersion}) so you may get unexpected behaviour"
        }
        return
    }

    # Now looks for where the property value being set has the same major and minor version as the supplied FrameworkVersion
    $majorMinorVersion = $FrameworkVersion -replace '(\d+\.\d+)\..*', '$1'
    $found = $False
    foreach ($outputElement in $outputElements) {
        $createPropertyElement = $outputElement.ParentNode
        if (-not $createPropertyElement -or $createPropertyElement.Name -ne "CreateProperty") {
            continue
        }

        # Check if the CreateProperty Value has the same major and minor version
        $currentVersion = $createPropertyElement.Value
        $currentMajorMinorVersion = $currentVersion -replace '(\d+\.\d+)\..*', '$1'
        if ($currentMajorMinorVersion -eq $majorMinorVersion) {
            $found = $True
            if ($currentVersion -eq $FrameworkVersion) {
                Write-SkippedLog "The runtime framework version is already set to '${FrameworkVersion}' in the props file at: '${FilePath}', skipping update"
            }
            else {
                $createPropertyElement.Value = $FrameworkVersion # Update to the new version
                Write-SuccessLog "The runtime framework version was updated from '${currentVersion}' to '${FrameworkVersion}' in the props file at: '${FilePath}'"
            }
        }
    }

    if ($found) {
        $xml.Save($FilePath)
    }
    else {
        $messagePrefix="No CreateProperty element setting the 'RuntimeFrameworkVersion' to version '${majorMinorVersion}.X' was found in the props file at: '${FilePath}'"
        if ($defaultVersion -eq $FrameworkVersion) {
            Write-InfoLog "${messagePrefix} but the default runtime framework version is already '${FrameworkVersion}' so should be okay"
        }
        else {
            Write-WarningLog "${messagePrefix} and the default runtime framework version (${defaultVersion}) does not match the desired version (${FrameworkVersion}) so you may get unexpected behaviour"
        }
        return
    }
}