@echo off
chcp 65001 >nul
cd /d "%~dp0\.."
echo ====================================================================
echo   INICIANDO SISTEMA EM MODO DEMONSTRACAO ("SUA MARCA")
echo   Dados: 2 meses de Comercio de Bebidas + Assistente IA Interativo
echo ====================================================================
python apresentacao_evento/rodar_demo.py
pause

