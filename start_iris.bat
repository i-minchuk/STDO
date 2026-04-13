@echo off
REM ============================================================
REM DokPotok IRIS - Стартовый скрипт для Windows
REM ============================================================
REM Использование:
REM   start_iris.bat              - Запуск в dev режиме (backend + frontend)
REM   start_iris.bat backend      - Только backend
REM   start_iris.bat frontend     - Только frontend
REM   start_iris.bat migrate      - Только миграции базы данных
REM   start_iris.bat full         - Полный запуск с проверками
REM ============================================================

setlocal EnableDelayedExpansion

REM Корень проекта (относительно этого файла)
set "PROJECT_ROOT=%~dp0"
set "FRONTEND_ROOT=%PROJECT_ROOT%frontend"
set "VENV_PATH=%PROJECT_ROOT%.venv"
set "VENV_PYTHON=%VENV_PATH%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"

REM Конфигурация по умолчанию
set "BACKEND_HOST=127.0.0.1"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=5173"
set "DB_DSN=postgresql://postgres:Qwerty852@localhost:5432/iris"
set "SECRET_KEY=iris-secret-key-change-in-production"
set "LOG_LEVEL=INFO"

REM Режим запуска (по умолчанию - dev)
set "MODE=%~1"
if "%MODE%"=="" set "MODE=dev"

echo ============================================================
echo DokPotok IRIS - Запуск в режиме: %MODE%
echo ============================================================
echo.

REM ============================================================
REM Проверка базовых условий
REM ============================================================

REM Проверка наличия main.py
if not exist "%PROJECT_ROOT%main.py" (
    echo [ОШИБКА] Файл main.py не найден в %PROJECT_ROOT%
    echo Проверьте, что вы запустили скрипт из директории STDO
    pause
    exit /b 1
)

REM Проверка наличия frontend
if not exist "%FRONTEND_ROOT%" (
    echo [ОШИБКА] Директория frontend не найдена: %FRONTEND_ROOT%
    pause
    exit /b 1
)

REM ============================================================
REM Режим: migrate - только миграции
REM ============================================================
if "%MODE%"=="migrate" (
    echo Запуск миграций базы данных...
    
    if not exist "%VENV_PYTHON%" (
        echo [ОШИБКА] Virtualenv не найден: %VENV_PYTHON%
        echo Сначала создайте виртуальное окружение:
        echo   python -m venv .venv
        echo   .venv\Scripts\activate
        echo   pip install -r requirements.txt
        pause
        exit /b 1
    )
    
    cd /d "%PROJECT_ROOT%"
    call "%VENV_ACTIVATE%"
    python -m alembic upgrade head
    
    if errorlevel 1 (
        echo [ОШИБКА] Миграции не выполнены
        pause
        exit /b 1
    )
    
    echo [OK] Миграции выполнены успешно
    pause
    exit /b 0
)

REM ============================================================
REM Режим: backend - только backend
REM ============================================================
if "%MODE%"=="backend" (
    echo Запуск backend сервера...
    echo.
    
    if not exist "%VENV_PYTHON%" (
        echo [ОШИБКА] Virtualenv не найден: %VENV_PYTHON%
        echo Сначала создайте виртуальное окружение:
        echo   python -m venv .venv
        echo   .venv\Scripts\activate
        echo   pip install -r requirements.txt
        pause
        exit /b 1
    )
    
    cd /d "%PROJECT_ROOT%"
    call "%VENV_ACTIVATE%"
    
    REM Проверяем миграции (не применяем автоматически)
    echo Проверка миграций...
    python -m alembic current >nul 2>&1
    if errorlevel 1 (
        echo [ВНИМАНИЕ] База данных требует миграций
        echo Запустите: python -m alembic upgrade head
        echo Или используйте: start_iris.bat migrate
        echo.
    )
    
    REM Запускаем uvicorn в текущем окне
    set "DB_DSN=%DB_DSN%"
    set "SECRET_KEY=%SECRET_KEY%"
    set "IRIS_LOG_LEVEL=%LOG_LEVEL%"
    python -m uvicorn main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload
    
    goto :eof
)

REM ============================================================
REM Режим: frontend - только frontend
REM ============================================================
if "%MODE%"=="frontend" (
    echo Запуск frontend сервера...
    echo.
    
    if not exist "%FRONTEND_ROOT%\package.json" (
        echo [ОШИБКА] package.json не найден: %FRONTEND_ROOT%\package.json
        pause
        exit /b 1
    )
    
    cd /d "%FRONTEND_ROOT%"
    
    REM Проверка node_modules
    if not exist "%FRONTEND_ROOT%\node_modules" (
        echo Установка зависимостей frontend...
        call npm install
        if errorlevel 1 (
            echo [ОШИБКА] Не удалось установить зависимости npm
            pause
            exit /b 1
        )
    )
    
    call npm run dev
    goto :eof
)

REM ============================================================
REM Режим: dev или full - полный запуск (backend + frontend)
REM ============================================================
if "%MODE%"=="dev" (
    echo Полный запуск (backend + frontend)
) else if "%MODE%"=="full" (
    echo Полный запуск с дополнительными проверками
) else (
    echo [НЕЗНАЕМЫЙ РЕЖИМ] %MODE%
    echo Доступные режимы: dev, backend, frontend, migrate, full
    pause
    exit /b 1
)

echo.
echo ============================================================
echo Шаг 1: Проверка зависимостей
echo ============================================================

REM Проверка Python venv
if not exist "%VENV_PYTHON%" (
    echo [ОШИБКА] Virtualenv не найден: %VENV_PYTHON%
    echo.
    echo Сначала создайте виртуальное окружение и установите зависимости:
    echo.
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    echo Или используйте скрипт setup:
    echo   scripts\setup_dev.bat
    echo.
    pause
    exit /b 1
)

REM Проверка PostgreSQL (проверяем порт 5432)
echo Проверка PostgreSQL...
netstat -ano 2>nul | findstr ":5432" >nul
if errorlevel 1 (
    echo [ВНИМАНИЕ] PostgreSQL не запущен или не слушает порт 5432
    echo Запустите PostgreSQL перед стартом приложения
    pause
    exit /b 1
)

echo [OK] PostgreSQL доступен

REM ============================================================
echo Шаг 2: Применение миграций
echo ============================================================

cd /d "%PROJECT_ROOT%"
call "%VENV_ACTIVATE%"

python -m alembic upgrade head
if errorlevel 1 (
    echo [ОШИБКА] Не удалось применить миграции
    echo Проверьте подключение к базе данных
    pause
    exit /b 1
)

echo [OK] Миграции применены

REM ============================================================
echo Шаг 3: Подготовка frontend
echo ============================================================

cd /d "%FRONTEND_ROOT%"

if not exist "node_modules" (
    echo Установка зависимостей frontend...
    call npm install
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить зависимости npm
        pause
        exit /b 1
    )
)

echo [OK] Frontend зависимости готовы

REM ============================================================
echo Шаг 4: Запуск backend
echo ============================================================

cd /d "%PROJECT_ROOT%"
call "%VENV_ACTIVATE%"

set "DB_DSN=%DB_DSN%"
set "SECRET_KEY=%SECRET_KEY%"
set "IRIS_LOG_LEVEL=%LOG_LEVEL%"

echo Запуск backend на http://%BACKEND_HOST%:%BACKEND_PORT%
echo API документация: http://%BACKEND_HOST%:%BACKEND_PORT%/docs
echo.

REM Запускаем backend в отдельном окне
start "DokPotok IRIS - Backend" cmd /k "cd /d \"%PROJECT_ROOT%\" && call \"%VENV_ACTIVATE%\" && set DB_DSN=%DB_DSN% && set SECRET_KEY=%SECRET_KEY% && set IRIS_LOG_LEVEL=%LOG_LEVEL% && python -m uvicorn main:app --host %BACKEND_HOST% --port %BACKEND_PORT% --reload"

REM Ждем пока backend запустится
echo Ожидание запуска backend...
timeout /t 10 /nobreak >nul

REM ============================================================
echo Шаг 5: Запуск frontend
echo ============================================================

cd /d "%FRONTEND_ROOT%"

echo Запуск frontend на http://localhost:%FRONTEND_PORT%
echo.

REM Запускаем frontend в отдельном окне
start "DokPotok IRIS - Frontend" cmd /k "cd /d \"%FRONTEND_ROOT%\" && npm run dev"

REM ============================================================
echo Шаг 6: Открытие браузера
echo ============================================================

timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo DokPotok IRIS запущен!
echo ============================================================
echo.
echo Backend:  http://%BACKEND_HOST%:%BACKEND_PORT%/docs
echo Frontend: http://localhost:%FRONTEND_PORT%
echo.
echo Окна серверов будут открыты в отдельныx терминалах.
echo Нажмите Ctrl+C в окнах для остановки серверов.
echo ============================================================
echo.

pause
exit /b 0