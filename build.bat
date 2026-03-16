@echo off
title FloppaAI — Build EXE
color 0C
echo.
echo  ========================================
echo   FloppaAI - Compilador para .EXE
echo  ========================================
echo.

echo [1/4] Instalando dependencias...
pip install customtkinter Pillow requests pyinstaller --quiet
if errorlevel 1 (
    echo ERRO ao instalar dependencias!
    pause
    exit /b 1
)

echo [2/4] Verificando icone...
if not exist "assets\icon.ico" (
    echo AVISO: assets\icon.ico nao encontrado.
    echo Coloque o arquivo icon.ico na pasta assets\ antes de buildar.
    echo Continuando sem icone...
)

echo [3/4] Compilando com PyInstaller...
if exist "assets\icon.ico" (
    pyinstaller --onefile --windowed --icon=assets\icon.ico --name=FloppaAI --add-data "assets;assets" --add-data "version.json;." app.py
) else (
    pyinstaller --onefile --windowed --name=FloppaAI --add-data "version.json;." app.py
)

if errorlevel 1 (
    echo ERRO na compilacao!
    pause
    exit /b 1
)

echo [4/4] Pronto!
echo.
echo  O arquivo FloppaAI.exe esta em: dist\FloppaAI.exe
echo.
explorer dist
pause
