@echo off
title FloppaAI — Iniciando...
color 0C
echo.
echo  =========================================
echo   FloppaAI - Floppa's Schoolhouse 2
echo  =========================================
echo.

set PYTHON=

:: 1. Tenta "py" (launcher universal do Windows)
py --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=py"
    goto found
)

:: 2. Tenta "python" no PATH
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=python"
    goto found
)

:: 3. Tenta "python3" no PATH
python3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON=python3"
    goto found
)

:: 4. Busca em pastas fixas por versao
for %%V in (313 312 311 310 39 38) do (
    if exist "%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe" (
        set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python%%V\python.exe"
        goto found
    )
    if exist "%PROGRAMFILES%\Python%%V\python.exe" (
        set "PYTHON=%PROGRAMFILES%\Python%%V\python.exe"
        goto found
    )
    if exist "C:\Python%%V\python.exe" (
        set "PYTHON=C:\Python%%V\python.exe"
        goto found
    )
)

:: 5. Busca dinamica em AppData
for /d %%D in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON=%%D\python.exe"
        goto found
    )
)

:: 6. Busca dinamica em Program Files
for /d %%D in ("%PROGRAMFILES%\Python*") do (
    if exist "%%D\python.exe" (
        set "PYTHON=%%D\python.exe"
        goto found
    )
)

:: 7. Instala automaticamente via winget
echo [!] Python nao encontrado. Instalando automaticamente...
echo     Aguarde, isso pode demorar alguns minutos...
echo.
winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo [ERRO] Nao foi possivel instalar automaticamente.
    echo        Baixe Python em: https://www.python.org/downloads/
    echo        Marque a opcao "Add Python to PATH" ao instalar!
    pause
    exit /b 1
)
:: Recarrega PATH
set "PYTHON=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if not exist "%PYTHON%" set PYTHON=python

:found
echo [OK] Python: %PYTHON%
echo.

:: Verifica dependencias
echo [*] Verificando dependencias...
"%PYTHON%" -c "import customtkinter, PIL, requests" >nul 2>&1
if errorlevel 1 (
    echo [*] Instalando dependencias, aguarde...
    "%PYTHON%" -m pip install customtkinter Pillow requests --quiet --disable-pip-version-check
    if errorlevel 1 (
        echo [*] Tentando com --user...
        "%PYTHON%" -m pip install customtkinter Pillow requests --user --quiet --disable-pip-version-check
        if errorlevel 1 (
            echo [ERRO] Falha ao instalar dependencias.
            echo        Execute manualmente: pip install customtkinter Pillow requests
            pause
            exit /b 1
        )
    )
    echo [OK] Dependencias instaladas!
    echo.
) else (
    echo [OK] Dependencias OK!
    echo.
)

:: Inicia o app
echo [OK] Iniciando FloppaAI...
cd /d "%~dp0"
start "" "%PYTHON%" app.py
exit
