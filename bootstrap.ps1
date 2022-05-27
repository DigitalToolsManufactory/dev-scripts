python -m venv .venv > $null
./.venv/Scripts/activate.ps1 > $null

pip install -r requirements.txt > $null

# create dev-scripts from template
$currentDir = $(Get-Location).toString().Replace("\", "/")
$content = Get-Content "./template.dev-scripts.ps1"
$content[0] = "`$__scripts_path = `"$currentDir`""
Set-Content "./dev-scripts.ps1" $content

# update user profile
$profileContent = Get-Content $PROFILE
$loadDevScripts = ". `"$currentDir/dev-scripts.ps1`""
if ( -not ($profileContent -contains $loadDevScripts)) {
    if ($profileContent.Length -gt 0) {
        $profileContent += ""
    }
    $profileContent += "###########################"
    $profileContent += "# Loading dev-env scripts #"
    $profileContent += $loadDevScripts
    $profileContent += "###########################"

    Set-Content $PROFILE $profileContent
}

deactivate > $null