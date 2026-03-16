@echo off
title FloppaAI — Modo Desenvolvedor
color 0A
cd /d "%~dp0"

echo.
echo  =====================================================
echo    FloppaAI — Modo Desenvolvedor
echo  =====================================================
echo.

REM ── SENHA DE ACESSO ───────────────────────────────────
set /p "SENHA=  Digite a senha de desenvolvedor: "
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
echo.
echo  Acesso liberado! Abrindo painel...
echo.
python dev_mode.py
if errorlevel 1 (
    echo.
    echo  [ERRO] Verifique se Python esta instalado.
    pause
)
