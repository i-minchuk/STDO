param(
    [ValidateSet("dev", "prod")]
    [string]$Mode = "dev"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$projectRoot  = "C:\Users\Novikova\Desktop\STDO\STDO"
$frontendRoot = Join-Path $projectRoot "frontend"
$venvPython   = Join-Path $projectRoot ".venv\Scripts\python.exe"
$venvActivate = Join-Path $projectRoot ".venv\Scripts\Activate.ps1"

$pgServiceName = "postgresql-x64-16"
$backendHost   = "127.0.0.1"
$backendPort   = 8000
$frontendPorts = @(5173, 5174, 5175)

function Wait-Port {
    param(
        [string]$HostName = "127.0.0.1",
        [int]$Port,
        [int]$TimeoutSeconds = 45
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    do {
        try {
            $ready = Test-NetConnection -ComputerName $HostName -Port $Port -InformationLevel Quiet -WarningAction SilentlyContinue
        }
        catch {
            $ready = $false
        }

        if ($ready) { return $true }
        Start-Sleep -Milliseconds 700
    }
    while ((Get-Date) -lt $deadline)

    return $false
}

try {
    # Проверка путей
    if (-not (Test-Path $projectRoot))       { throw "Project root not found: $projectRoot" }
    if (-not (Test-Path $frontendRoot))      { throw "Frontend folder not found: $frontendRoot" }
    if (-not (Test-Path $venvPython))        { throw "Virtualenv python not found: $venvPython" }
    if (-not (Test-Path $venvActivate))      { throw "Virtualenv activation script not found: $venvActivate" }
    if (-not (Test-Path (Join-Path $frontendRoot "package.json"))) { throw "frontend\package.json not found" }
    if (-not (Test-Path (Join-Path $projectRoot  "main.py")))      { throw "main.py not found in project root" }

    # npm
    $npmCmd = $null
    try {
        $npmCmd = (Get-Command npm.cmd -ErrorAction Stop).Source
    }
    catch {
        try {
            $npmCmd = (Get-Command npm -ErrorAction Stop).Source
        }
        catch {
            throw "npm / npm.cmd not found in PATH"
        }
    }

    # PostgreSQL
    $svc = Get-Service -Name $pgServiceName -ErrorAction Stop
    if ($svc.Status -ne "Running") {
        Start-Service -Name $pgServiceName
        $svc.WaitForStatus("Running", "00:00:20")
    }

    # venv + миграции
    Set-Location $projectRoot
    & $venvActivate

    & $venvPython -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic migrations failed"
    }

    # node_modules
    $nodeModules = Join-Path $frontendRoot "node_modules"
    if (-not (Test-Path $nodeModules)) {
        Push-Location $frontendRoot
        & $npmCmd install
        $npmInstallExit = $LASTEXITCODE
        Pop-Location
        if ($npmInstallExit -ne 0) {
            throw "npm install failed"
        }
    }

    # backend
    $backendArgs = @("-m", "uvicorn", "main:app", "--host", $backendHost, "--port", "$backendPort")
    if ($Mode -eq "dev") {
        $backendArgs += "--reload"
    }

    Start-Process -FilePath $venvPython -ArgumentList $backendArgs -WorkingDirectory $projectRoot -WindowStyle Hidden | Out-Null

    # frontend (один нормальный запуск через npm)
    $frontendPort = $null

    if ($Mode -eq "dev") {
        Start-Process -FilePath $npmCmd `
            -ArgumentList @("run", "dev") `
            -WorkingDirectory $frontendRoot `
            -WindowStyle Minimized | Out-Null
    }

    # ожидание backend
    $backendReady = Wait-Port -HostName $backendHost -Port $backendPort -TimeoutSeconds 45
    if (-not $backendReady) {
        throw "Backend port did not open in time"
    }

    # определение порта фронта
    if ($Mode -eq "dev") {
        foreach ($p in $frontendPorts) {
            if (Wait-Port -HostName "127.0.0.1" -Port $p -TimeoutSeconds 20) {
                $frontendPort = $p
                break
            }
        }
    }

    # открытие браузера
    Start-Process "http://$backendHost`:$backendPort/docs" | Out-Null

    if ($frontendPort) {
        Start-Process "http://localhost:$frontendPort" | Out-Null
    }
    elseif ($Mode -eq "dev") {
        Start-Process "http://localhost:5173" | Out-Null
    }
}
catch {
    Add-Type -AssemblyName PresentationFramework
    [System.Windows.MessageBox]::Show($_.Exception.Message, 'STDO launcher error', 'OK', 'Error') | Out-Null
    exit 1
}