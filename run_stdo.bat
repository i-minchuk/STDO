@echo off
REM Запуск ДокПоток IRIS (бэкенд + уже собранный фронтенд)

REM Переходим в корень проекта
cd /d C:\Users\Novikova\Desktop\STDO\STDO

echo Проверка PostgreSQL...
sc query | findstr /I "postgresql"

echo Запуск ДокПоток IRIS на http://127.0.0.1:8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause