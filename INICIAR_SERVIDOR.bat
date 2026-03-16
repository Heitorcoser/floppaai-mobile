@echo off
title FloppaAI — Servidor Admin
color 0A
cd /d "%~dp0"

echo.
echo  =====================================================
echo    FloppaAI — Painel Administrativo
echo  =====================================================
echo.
set /p "SENHA=  Senha: "
if not "%SENHA%"=="Heitor@cris" (
    color 0C
    echo.
    echo  =====================================================
    echo    ACESSO NEGADO! Senha incorreta.
    echo  =====================================================
    echo.
    timeout /t 3 /nobreak >nul
    exit
)
color 0A
echo   Acesso liberado!
echo.

REM Mata processos antigos
taskkill /F /IM ngrok.exe >nul 2>&1
timeout /t 1 /nobreak >nul

REM Configura token do ngrok
echo  [1/3] Configurando ngrok...
"%~dp0ngrok.exe" config add-authtoken 3AzPTtYtsCKbxmKUL5bW5VHO2Rm_7SoNsUEt6KZDtJZQV5bZP >nul 2>&1

REM Inicia servidor Python
echo  [2/3] Iniciando servidor (porta 8080)...
start "FloppaAI Server" cmd /k "cd /d %~dp0 && python server.py"
timeout /t 2 /nobreak >nul

REM Inicia ngrok
echo  [3/3] Iniciando ngrok...
start "FloppaAI ngrok" cmd /k "%~dp0ngrok.exe http 8080"
timeout /t 3 /nobreak >nul

echo.
echo  =====================================================
echo   PRONTO! Servidor online.
echo.
echo   A URL do celular aparece na janela "FloppaAI ngrok"
echo   linha "Forwarding":
echo   https://xxxx.ngrok-free.app
echo.
echo   Cole essa URL no Dev Mode ^ Configuracoes ^ URL Automatica
echo   Todos os PCs e celulares vao se conectar sozinhos!
echo  =====================================================
echo.
pause
