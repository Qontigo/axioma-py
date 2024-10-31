#!/usr/bin/env pwsh
#
# NOTE: This file is maintained in the Qontigo/devops-gh-actions repo (scripts/common/core-utilities.psm1) and that copy will overwrite any changes made in any repo using the file
#       If changes are necessary to this file then you will need to raise a PR in that repo and perform appropriate testing with repos which use this file

# Powershell utility functions
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

function Invoke-ExpressionSafely{
    <#
    .SYNOPSIS
         Invoke an expression and catch (and log) any errors

    .PARAMETER Cmd
        The command to execute

    .PARAMETER IgnoreExitCodes
        Array of exit codes to ignore for the purposes of failing/not failing the invocation
    #>
    [CmdletBinding(PositionalBinding=$True)]
    param (
        [Parameter(Mandatory,ValueFromPipeline=$True)]
        [string]$Cmd,
        [Parameter(Mandatory=$False)]
        $IgnoreExitCodes = @()
    )

    try {
        Write-InfoLog "Executing: $Cmd"
        Invoke-Expression $Cmd
        $lec = $LastExitCode

        if (0 -ne $lec) {
            if ($lec -notin $IgnoreExitCodes) {
                $msg = ("Non-0 exit code ({0}) returned by ""{1}"" - see output above for error details" -f $lec, $Cmd)
                Write-ErrorLog "${msg}"
                throw $msg
            }
            else {
                Write-DebugLog ("Non-0 exit code ({0}) returned by ""{1}"" but this is in the ignore list, so not failing" -f $lec, $Cmd)
            }
        }
    }
    catch
    {
        $ErrorMessage = $_
        Write-ErrorLog ("${Cmd} failed' - ${ErrorMessage}")
        Write-Error -Message $ErrorMessage
        exit 1
    }
}
