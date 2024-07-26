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

function ConvertFrom-ArrayString {
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

        foreach ($a in @('[ "foo bar", "baz" ]' | ConvertFrom-ArrayString)) {
            Write-Host "- $a"
        }

    .EXAMPLE
        # CSV array string => Powershell array

        $array = @('foo bar,baz' | ConvertFrom-ArrayString -Separator ",")
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
         foreach ($a in @($array | ConvertFrom-ArrayString -Separator "<none>")) {
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

function ConvertFrom-Object {
    <#
    .SYNOPSIS
         Converts an object to a dictionary of key-value pairs

    .DESCRIPTION
      # Converts an object to a dictionary of key-value pairs
        Each key is the full path to the value:
         - for a root level property "foo" the key would be "foo"
         - for a nested property foo { bar: "baz" } the key would be "foo.bar"

    .PARAMETER Object
        The object to convert

    .PARAMETER Parent
        The parent property name - should not normally be user-supplied

    .PARAMETER BoolToString
        Optionally convert booleans to strings

    .OUTPUTS
        A flattened dictionary of the supplied JSON object

    .EXAMPLE

    #>
    [CmdletBinding(PositionalBinding=$True)]
    param (
        [Parameter(Mandatory=$False, Position=0)]
        [PSCustomObject]$Object=$Null,
        [Parameter(Mandatory=$false)]
        [string]$Parent = "",
        [Parameter(Mandatory=$false)]
        [switch]$BoolToString = $False
    )

    $properties = @{}
    if ($Null -ne $Object) {
        foreach ($property in $Object.PSObject.Properties) {
            $key = if ($Parent) { "$Parent.$($property.Name)" } else { $property.Name }

            if ($property.Value -is [PSCustomObject]) {
                $properties += ConvertFrom-Object -Object $property.Value -Parent $key -BoolToString:$BoolToString
            }
            else {
                if ($BoolToString -and $property.Value -is [bool]) {
                    $property.Value = $property.Value.ToString().ToLower()
                }
                $properties[$key] = $property.Value
            }
        }
    }
    return $properties
}

function ConvertFrom-JsonString {
    <#
    .SYNOPSIS
         Converts a JSON object string to a dictionary of key-value pairs

    .DESCRIPTION
      # Converts a JSON object to a dictionary of key-value pairs
        Each key is the full path to the value:
         - for a root level property "foo" the key would be "foo"
         - for a nested property foo { bar: "baz" } the key would be "foo.bar"

    .PARAMETER Json
        The json object string to convert

    .PARAMETER Parent
        The parent property name - should not normally be user-supplied

    .OUTPUTS
        A flattened dictionary of the supplied JSON object

    .EXAMPLE
        # JSON array string => Powershell array

        foreach ($a in @('[ "foo bar", "baz" ]' | ConvertFrom-ArrayString)) {
            Write-Host "- $a"
        }

    #>
    [CmdletBinding(PositionalBinding=$True)]
    param (
        [Parameter(Mandatory=$True, ValueFromPipeline=$True, Position=0)]
        [string]$Json,
        [Parameter(Mandatory=$false)]
        [string]$Parent = ""
    )

    $jsonObject = $Null
    try {
        $jsonObject = ConvertFrom-Json -InputObject $Json -ErrorAction Stop
    }
    catch {
        throw [System.ArgumentException]::new("JSON validation failed: $($_.Exception.Message), input: $Json", "`$Json")
    }
    if ($jsonObject -is [System.Array]) {
        throw [System.ArgumentException]::new("The supplied object is a JSON array - this is not supported.", "`$Json")
    }

    ConvertFrom-Object $jsonObject -BoolToString
}

  function ConvertTo-CrossPlatformPath {
    <#
    .SYNOPSIS
         Converts a path to a cross-platform version

    .PARAMETER Path
        The Path to convert

    .PARAMETER Root
        Optional root prefix to add - eg. if the input was c:\foo we might want to map this to /mnt/c/foo

    .OUTPUTS
        The cross-platform version of the path

    .EXAMPLE
        Write-Host ("C:\foo" | ConvertTo-CrossPlatformPath)

    .EXAMPLE
        ConvertTo-CrossPlatformPath "C:\foo" "/mnt"
    #>
    [CmdletBinding(PositionalBinding=$True)]
    param (
        [Parameter(Mandatory=$False, ValueFromPipeline=$True, Position=0)]
        [string]$Path="",
        [Parameter(Mandatory=$False, Position=1)]
        [string]$Root=""
    )

    $Path=$Path.Replace('\', '/')
    # Remove colon and add a leading / if necessary - e.g C:/ => /c
    if ($Path -match ":") {
        $drive = $Path.Split(':')[0]
        $Path = "/$($drive.ToLower())$($path.Split(':')[1])"
    }

    if ("" -ne $Root) {
        if (-not $Path.StartsWith("/")) {
            $Root += "/"
        }
    }
    return "${Root}${Path}"
  }
