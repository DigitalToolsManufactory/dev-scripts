python -m venv .venv
./.venv/Scripts/activate.ps1

pip install -r requirements.txt

$currentDir = $(Get-Location).toString().Replace("\", "/")
$content = Get-Content "./template.dev-scripts.ps1"
$content[0] = "`$__scripts_path = `"$currentDir`""
Set-Content "./dev-scripts.ps1" $content

deactivate