@echo off
echo LinkedIn Automator Toolkit
echo =========================
echo.
echo 1) Run LinkedIn Automator GUI
echo 2) Run Post Format Test (mock version - no API needed)
echo 3) Check Gemini API Configuration
echo 4) Run Full LinkedIn Automator
echo 5) Exit
echo.

set /p choice=Enter your choice (1-5): 

if "%choice%"=="1" (
    echo Starting LinkedIn Automator GUI...
    python gui/run_gui.py
) else if "%choice%"=="2" (
    echo Starting Post Format Test (mock version)...
    python test_gui_logging_mock.py
) else if "%choice%"=="3" (
    echo Checking Gemini API Configuration...
    python check_gemini_api.py
    pause
) else if "%choice%"=="4" (
    echo Starting Full LinkedIn Automator...
    python start_linkedin_automator.py
) else if "%choice%"=="5" (
    echo Exiting...
    exit
) else (
    echo Invalid choice. Please try again.
    pause
    start_tools.bat
) 