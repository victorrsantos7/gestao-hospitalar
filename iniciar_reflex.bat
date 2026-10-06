@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente Reflex nao encontrado em .venv.
    echo Crie o ambiente e instale as dependencias antes de iniciar.
    pause
    exit /b 1
)

echo Iniciando Sistema de Gestao Hospitalar...
echo Acesse http://localhost:3000

echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { Set-Location -LiteralPath '%~dp0'; & '.\.venv\Scripts\python.exe' -m reflex run --env prod --single-port 2>&1 | Tee-Object -FilePath 'reflex.log' }"

endlocal
