@echo off
REM ============================================================
REM DokPotok IRIS - Скрипт установки зависимостей для Windows
REM ============================================================

setlocal EnableDelayedExpansion

set "PROJECT_ROOT=%~dp0.."
set "VENV_PATH=%PROJECT_ROOT%.venv"
set "VENV_PYTHON=%VENV_PATH%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"
set "FRONTEND_ROOT=%PROJECT_ROOT%frontend"

echo ============================================================
echo DokPotok IRIS - Установка зависимостей
echo ============================================================
echo.

REM Проверка Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден в PATH
    echo Установите Python 3.12+ или активируйте виртуальное окружение
    pause
    exit /b 1
)

echo Шаг 1: Проверка/создание виртуального окружения
echo.

if not exist "%VENV_PYTHON%" (
    echo Создаю виртуальное окружение в .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение
        pause
        exit /b 1
    )
    echo [OK] Виртуальное окружение создано
) else (
    echo [OK] Виртуальное окружение уже существует
)

echo.
echo Шаг 2: Активация виртуального окружения
echo.

call "%VENV_ACTIVATE%"

echo.
echo Шаг 3: Обновление pip
echo.

python -m pip install --upgrade pip --quiet

echo.
echo Шаг 4: Установка backend зависимостей
echo.

if exist "%PROJECT_ROOT%requirements.txt" (
    pip install -r "%PROJECT_ROOT%requirements.txt"
    if errorlevel 1 (
        echo [ОШИБКА] Не удалось установить backend зависимости
        pause
        exit /b 1
    )
    echo [OK] Backend зависимости установлены
) else (
    echo [ВНИМАНИЕ] requirements.txt не найден
)

echo.
echo Шаг 5: Установка dev зависимостей (опционально)
echo.

if exist "%PROJECT_ROOT%requirements-dev.txt" (
    pip install -r "%PROJECT_ROOT%requirements-dev.txt" --quiet
    if errorlevel 1 (
        echo [ВНИМАНИЕ] Не все dev зависимости установлены
    ) else (
        echo [OK] Dev зависимости установлены
    )
)

echo.
echo Шаг 6: Установка frontend зависимостей
echo.

if exist "%FRONTEND_ROOT%\package.json" (
    cd /d "%FRONTEND_ROOT%"
    
    if not exist "node_modules" (
        echo Установка npm зависимостей...
        call npm install
        if errorlevel 1 (
            echo [ОШИБКА] Не удалось установить npm зависимости
            pause
            exit /b 1
        )
        echo [OK] Frontend зависимости установлены
    ) else (
        echo [OK] Frontend зависимости уже установлены
    )
    
    cd /d "%PROJECT_ROOT%"
) else (
    echo [ВНИМАНИЕ] package.json не найден в frontend
)

echo.
echo ============================================================
echo Установка завершена!
echo ============================================================
echo.
echo Для запуска приложения используйте:
echo   start_iris.bat
echo.
echo Или отдельно:
echo   start_iris.bat backend    - Backend сервер
echo   start_iris.bat frontend   - Frontend сервер
echo   start_iris.bat migrate    - Миграции БД
echo.
echo ============================================================
pause
