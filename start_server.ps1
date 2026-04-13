$env:DB_DSN='postgresql://postgres:Qwerty852@localhost:5432/iris'
$env:SECRET_KEY='test-key-for-dev-only-min-32-chars'
$env:IRIS_LOG_LEVEL='DEBUG'

cd STDO

Write-Host "Starting DokPotok IRIS..."
Write-Host "DB_DSN: $env:DB_DSN"

python -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 | Out-File -FilePath "uvicorn.log" -Append
Write-Host "Server logs written to uvicorn.log"
