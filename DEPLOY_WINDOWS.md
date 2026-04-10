Памятка по локальному запуску (dev) на Windows 11

1. Назначение
Этот сценарий поднимает полное dev‑окружение STDO/IRIS на твоём ноутбуке:

PostgreSQL (служба Windows)

backend (FastAPI + Uvicorn с --reload)

frontend (Vite dev‑сервер npm run dev)

Dev‑режим даёт автоперезапуск backend при изменениях кода (--reload) и горячую перезагрузку фронта. В продакшене --reload использовать нельзя.

2. Файлы для запуска
В корне проекта C:\Users\Novikova\Desktop\STDO\STDO лежат:

start_iris.ps1 — основной dev‑launcher (PowerShell)

start_iris.bat — обёртка для запуска .ps1 двойным кликом

Все старые стартовые скрипты (build_and_run_stdo.bat, scripts\setup_dev.ps1) не используются.

3. Быстрый запуск: двойной клик
Открой Проводник →
C:\Users\Novikova\Desktop\STDO\STDO

Дважды кликни по start_iris.bat.

Откроется окно PowerShell и запустится скрипт start_iris.ps1.

Что делает launcher:

проверяет структуру проекта и .venv;

проверяет наличие npm / npm.cmd;

запускает службу PostgreSQL (postgresql-x64-16);

активирует виртуальное окружение .venv;

прогоняет alembic upgrade head;

при отсутствии node_modules делает npm install во frontend;

запускает backend:

powershell
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
(dev‑режим с авто‑reload);

запускает frontend:

powershell
npm run dev
(Vite dev‑сервер, обычно на http://localhost:5173);

ждёт, пока порты поднимутся, и открывает в браузере:

Swagger: http://127.0.0.1:8000/docs

frontend: http://localhost:<порт> (5173 или следующий свободный).

4. Запуск из PowerShell вручную
Альтернатива двойному клику — запуск из консоли:

powershell
cd C:\Users\Novikova\Desktop\STDO\STDO

# при необходимости разово в сессии:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

.\start_iris.ps1 -Mode dev
Опция -Mode dev включает dev‑режим (backend с --reload, frontend dev‑сервер).

5. Что считается успешным стартом
В окне лаунчера в конце выводится блок:

text
===== FINAL STATUS =====
Mode:      dev
Backend:   http://127.0.0.1:8000
Docs:      http://127.0.0.1:8000/docs
Frontend:  http://localhost:5173   (или другой порт)
Postgres:  postgresql-x64-16
========================
И автоматически открываются:

http://127.0.0.1:8000/docs — backend работает;

http://localhost:5173 (или порт, указанный в статусе) — фронтенд работает.

6. Остановка dev‑окружения
Закрыть окна PowerShell, которые были открыты для:

backend (Uvicorn),

frontend (npm run dev),

сам launcher (при желании).

Служба PostgreSQL останется запущенной (это нормально для dev).

При следующем запуске start_iris.ps1 сам проверит состояние Postgres и не будет перезапускать её лишний раз.