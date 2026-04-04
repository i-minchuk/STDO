Param()

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not available in PATH. Activate your conda or virtual environment first."
    exit 1
}

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
python -m pre_commit install

Write-Host "Python development environment ready."
Write-Host "Run 'cd frontend; npm ci' separately if you need frontend dependencies."
