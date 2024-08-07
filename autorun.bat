@echo off

REM Check if the operating system is Windows
if "%OS%"=="Windows_NT" (
    REM Check if Python is installed and version is 3.11 or higher
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "delims=" %%v in ('python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2]))))"') do set "python_version=%%v"
        setlocal enabledelayedexpansion
        set "python_version=!python_version:~0,-2!"
        if %python_version% GEQ 3.11 (
            echo Python 3.11 or higher is already installed.
            pip3 install -r requirements.txt
            echo Installing requirements
            set "FLASK_APP=app.py"
            echo Exporting FLASK_APP environment variable
            set "FLASK_ENV=development"
            echo Exporting FLASK_ENV environment variable

            flask db init
            echo Initializing database
            flask db migrate -m "Add organisation_email to Organisation"
            echo Migrating database
            flask db upgrade
            echo Upgrading database

            echo Running the application...
            flask run
        ) else (
            echo Python version is below 3.11. Installing Python...
            REM Install Python on Windows
            choco install python --version=3.11

            REM Verify if Python is installed again
            where python3 >nul 2>&1
            if %errorlevel% equ 0 (
                for /f "delims=" %%v in ('python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2]))))"') do set "python_version=%%v"
                setlocal enabledelayedexpansion
                set "python_version=!python_version:~0,-2!"
                if %python_version% GEQ 3.11 (
                    echo Python 3.11 or higher is installed.
                    pip3 install -r requirements.txt
                ) else (
                    echo Python installation failed. Exiting...
                    exit /b 1
                )
            ) else (
                echo Python installation failed. Exiting...
                exit /b 1
            )
        )
    ) else (
        echo Python is not installed. Exiting...
        exit /b 1
    )

    echo Running autorun.bat...
    call autorun.bat
) else (
    REM Run autorun.sh on macOS or Linux
    echo Running autorun.sh...
    sh autorun.sh
)
