@echo off
title FloppaAI - Gerar Icone
echo Instalando Pillow...
pip install Pillow --quiet
echo Gerando icones...
python make_icon.py
pause
