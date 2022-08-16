$__scripts_path = ""

function _current_dir()
{
    $currentDir = $( Get-Location ).toString().Replace("\", "/")
    return "`"$currentDir`""
}

function dev()
{
    Invoke-Expression "$__scripts_path/.venv/Scripts/activate.ps1" > $null

    Invoke-Expression "python $__scripts_path/dev.py $args"

    Invoke-Expression "deactivate" > $null
}

function gch()
{
    Invoke-Expression "$__scripts_path/.venv/Scripts/activate.ps1" > $null

    $current_dir = _current_dir
    Invoke-Expression "python $__scripts_path/gch.py --project $current_dir" > $null

    Invoke-Expression "deactivate" > $null
}

function fsc()
{
    Invoke-Expression "$__scripts_path/.venv/Scripts/activate.ps1" > $null

    $current_dir = _current_dir
    Invoke-Expression "python $__scripts_path/fsc.py --project $current_dir" > $null

    Invoke-Expression "deactivate" > $null
}