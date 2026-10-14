@echo off
setlocal

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Ambiente Reflex nao encontrado em .venv.
    echo Crie o ambiente e instale as dependencias antes de iniciar.
    pause
    exit /b 1
)

echo Executando verificacao previa...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\preflight.ps1"
if errorlevel 1 (
    echo.
    echo Preflight reprovado. A aplicacao nao foi iniciada.
    pause
    exit /b 1
)

echo Iniciando Sistema de Gestao Hospitalar...
echo Acesse http://localhost:3000

if "%XANO_API_URL%"=="" set "XANO_API_URL=https://x8ki-letl-twmt.n7.xano.io/api:3lVm5Wbj"
if "%XANO_TIMEOUT_SECONDS%"=="" set "XANO_TIMEOUT_SECONDS=10"
if "%GESTAO_LOG_FILE%"=="" set "GESTAO_LOG_FILE=logs\gestao_hospitalar.log"
if "%GESTAO_LOG_LEVEL%"=="" set "GESTAO_LOG_LEVEL=INFO"
echo Log: %GESTAO_LOG_FILE% (nivel %GESTAO_LOG_LEVEL%)

if not exist "logs" mkdir "logs"
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command "& { Set-Location -LiteralPath '%~dp0'; & '.\.venv\Scripts\python.exe' -m reflex run --env prod --single-port --frontend-port 3000 --backend-host 127.0.0.1 2>&1 | Tee-Object -FilePath 'logs\reflex.log' }"

endlocal
