#!/usr/bin/env pwsh

# Common powershell functions

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

function Convert-FromArrayString {
    <#
    .SYNOPSIS
         Converts a string representation of multiple values to a powershell array

    .DESCRIPTION
      # Converts strings in a variety of formats to a powershell array:
        - JSON array strings - [ "one", "two" ]
        - One item per line in a multi-line string
        - items separated by a separator (default: space)

    .PARAMETER InputString
        The string to convert

    .PARAMETER Separator
        Optional separator between elements if it is NOT a JSON array.  Defaults to space in addition to newline.
        Set to <none> if each line should be considered a separate entry

    .OUTPUTS
        The array representation of the input string

    .EXAMPLE
        # JSON array string => Powershell array

        foreach ($a in @('[ "foo bar", "baz" ]' | Convert-FromArrayString)) {
            Write-Host "- $a"
        }

    .EXAMPLE
        # CSV array string => Powershell array

        $array = @('foo bar,baz' | Convert-FromArrayString -Separator ",")
        foreach ($a in $array) {
            Write-Host "- $a"
        }

    .EXAMPLE
        # Multi-line string => Powershell array
        # `-Separator "<none>"` is required to ensure "foo bar" is considered a single element

        $array = @"
        foo bar
        baz
        "@
         foreach ($a in @($array | Convert-FromArrayString -Separator "<none>")) {
            Write-Host "- $a"
        }
    #>
    [CmdletBinding(PositionalBinding=$True)]
    param (
        [Parameter(Mandatory=$False, ValueFromPipeline=$True, Position=0)]
        [string]$InputString="",
        [Parameter(Mandatory=$False, Position=1)]
        [string]$Separator = " "
    )

    # Initialize an array to hold the results
    $array = @()
    if (0 -eq $InputString.Trim().Length) {
        return $array
    }

    # Check if the input is a JSON array
    if ($InputString.StartsWith("[") -and $InputString.EndsWith("]")) {
        # Input is a JSON array
        $jsonArray = $InputString | ConvertFrom-Json
        foreach ($item in $jsonArray) {
            $array += $item
        }
    }
    else {
        # Input is a multi-line string
        $lines = $InputString -split "`n"
        foreach ($line in $lines) {
            # Strip leading and trailing spaces from each line
            $line = $line.Trim()
            if ($Separator -eq "<none>") {
                $array += $line
            } else {
                $parts = $line -split $Separator
                foreach ($part in $parts) {
                    if (-not [string]::IsNullOrWhiteSpace($part)) {
                        $array += $part
                    }
                }
            }
        }
    }
    $array
}
