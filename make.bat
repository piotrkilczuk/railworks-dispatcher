@echo off

if "%1"=="binary" (
    pyinstaller --clean --onefile dispatcher.py
	start explorer dist
)

if "%1"=="virtualenv" (
    @deactivate
	rm -rf venv
	virtualenv -p C:\Python27\Python.exe venv
	venv\Scripts\easy_install "http://downloads.sourceforge.net/project/pywin32/pywin32/Build 219/pywin32-219.win-amd64-py2.7.exe"
	venv\Scripts\pip install Jinja2==2.7.3 pyinstaller==2.1
)
