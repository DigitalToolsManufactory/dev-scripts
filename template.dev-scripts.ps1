$__scripts_path = ""

function _current_dir()
{
    $currentDir = $( Get-Location ).toString().Replace("\", "/")
    return "`"$currentDir`""
}

function gch()
{
    Invoke-Expression "$__scripts_path/.venv/Scripts/activate.ps1" > $null

    $current_dir = _current_dir
    Invoke-Expression "python $__scripts_path/gch.py --repository-path $current_dir" > $null

    Invoke-Expression "deactivate" > $null
}