cd STDO
python -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 | Tee-Object -FilePath server.log
