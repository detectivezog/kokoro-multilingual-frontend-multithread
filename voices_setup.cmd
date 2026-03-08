@echo off
echo - - - Running - - -
cd /d "%~dp0"
cd ./voice_manager
python voice_setup.py
timeout /t 10
