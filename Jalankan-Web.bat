@echo off
setlocal
cd /d "%~dp0"
py -3 -c "import sqlite3" >nul 2>nul
if not errorlevel 1 goto installed_py
python -c "import sqlite3" >nul 2>nul
if not errorlevel 1 goto installed_python
set "ruangcatatPython=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%ruangcatatPython%" goto bundled
 echo Python tidak ditemukan. Pasang Python 3.10 atau lebih baru.
pause
exit /b 1

:installed_py
if "%~1"=="--check" (
    py -3 -c "import sqlite3; print('RuangCatat web siap dijalankan.')"
    exit /b
)
py -3 run_web.py
goto finished

:installed_python
if "%~1"=="--check" (
    python -c "import sqlite3; print('RuangCatat web siap dijalankan.')"
    exit /b
)
python run_web.py
goto finished

:bundled
if "%~1"=="--check" (
    "%ruangcatatPython%" -c "import sqlite3; print('RuangCatat web siap dijalankan dengan Python bawaan Codex.')"
    exit /b
)
"%ruangcatatPython%" run_web.py

:finished
if errorlevel 1 pause
