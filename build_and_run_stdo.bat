@echo off
REM ============================================
REM  ДокПоток IRIS: сборка фронтенда + запуск бэкенда
REM  Удобный старт одним двойным кликом
REM ============================================

REM --- 0. Настройки путей ---
set PROJECT_ROOT=C:\Users\Novikova\Desktop\STDO\STDO
set FRONTEND_DIR=%PROJECT_ROOT%\frontend
set URL=http://127.0.0.1:8000

REM --- 1. Проверка наличия Python и uvicorn ---
where python >nul 2>nul
IF ERRORLEVEL 1 (
    echo [ОШИБКА] Python не найден в PATH.
    echo Установи Python 3.12 и перезапусти окно.
    pause
    exit /b 1
)

REM Проверяем uvicorn
python -m uvicorn --version >nul 2>nul
IF ERRORLEVEL 1 (
    echo Устанавливаю uvicorn...
    pip install "uvicorn[standard]"
)

REM --- 2. Сборка фронтенда ---
echo.
echo ==============================
echo [1/3] СБОРКА ФРОНТЕНДА
echo ==============================
cd /d %FRONTEND_DIR%

where npm >nul 2>nul
IF ERRORLEVEL 1 (
    echo [ОШИБКА] npm не найден. Установи Node.js (https://nodejs.org) и перезапусти.
    pause
    exit /b 1
)

IF NOT EXIST node_modules (
    echo node_modules не найден. Устанавливаю зависимости (npm install)...
    npm install
    IF ERRORLEVEL 1 (
        echo [ОШИБКА] npm install завершился с ошибкой.
        pause
        exit /b 1
    )
) ELSE (
    echo Зависимости уже установлены. Пропускаю npm install.
)

echo Запускаю npm run build...
npm run build
IF ERRORLEVEL 1 (
    echo [ОШИБКА] Сборка фронтенда (npm run build) завершилась с ошибкой.
    pause
    exit /b 1
)

REM --- 3. Запуск бэкенда (uvicorn) ---
echo.
echo ==============================
echo [2/3] ЗАПУСК БЭКЕНДА (uvicorn)
echo ==============================
cd /d %PROJECT_ROOT%

echo Проверка службы PostgreSQL (если есть)...
sc query | findstr /I "postgresql"

echo Запускаю ДокПоток IRIS на %URL%
start "" cmd /c "python -m uvicorn main:app --host 0.0.0.0 --port 8000"

REM Небольшая пауза, чтобы сервер успел подняться
timeout /t 5 >nul

REM --- 4. Открываем браузер ---
echo.
echo ==============================
echo [3/3] ОТКРЫТИЕ БРАУЗЕРА
echo ==============================

REM Пытаемся открыть через системную команду "start"
start "" "%URL%"

set COMET_PATH="C:\Users\Novikova\AppData\Local\Perplexity\Comet\Application\comet.exe"

IF EXIST %COMET_PATH% (
    start "" %COMET_PATH% %URL%
) ELSE (
    echo [ВНИМАНИЕ] Comet по пути %COMET_PATH% не найден.
    echo Открой вручную в браузере: %URL%
)

echo Готово. Сервер запущен, браузер открыт.
echo Закрой это окно, если оно больше не нужно.
pause