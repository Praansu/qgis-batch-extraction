@echo off
title Chainage Extraction Pipeline
setlocal enabledelayedexpansion

:: ============================================================
::  Chainage Extraction — QGIS Batch Pipeline
::  Drag your project folder onto this batch file, or
::  double-click and type/paste the path when prompted.
:: ============================================================

:: --- Auto-detect QGIS Python launcher -----------------------
set "QGIS_PY="
if exist "C:\OSGeo4W\bin\python-qgis-ltr.bat" set "QGIS_PY=C:\OSGeo4W\bin\python-qgis-ltr.bat"
if exist "C:\OSGeo4W\bin\python-qgis.bat"       set "QGIS_PY=C:\OSGeo4W\bin\python-qgis.bat"

if "%QGIS_PY%"=="" (
    echo [ERROR] QGIS Python not found.
    echo   Install QGIS LTR from: https://qgis.org/download/
    pause
    exit /b 1
)

:: --- Get project folder -------------------------------------
set "PROJ=%~1"
if "%PROJ%"=="" (
    echo.
    echo Enter project folder path ^(or drag folder here and press Enter^):
    set /p "PROJ=> "
)

:: Strip surrounding quotes if any
set PROJ=%PROJ:"=%

:: Strip trailing backslash
if "%PROJ:~-1%"=="\" set PROJ=%PROJ:~0,-1%

:: --- Validate -----------------------------------------------
if not exist "%PROJ%" (
    echo.
    echo [ERROR] Folder not found: %PROJ%
    pause
    exit /b 1
)

:: --- Resolve paths ------------------------------------------
set "SCRIPT=%~dp0chainage_extraction.py"
set "OUTDIR=%~dp0output_chainage"
if not exist "%OUTDIR%" mkdir "%OUTDIR%"

echo.
echo  Project : %PROJ%
echo  Output  : %OUTDIR%\%~nx1\
echo.

:: --- Run ----------------------------------------------------
"%QGIS_PY%" "%SCRIPT%" "%PROJ%" "%OUTDIR%"

echo.
if %ERRORLEVEL% equ 0 (
    echo Done. Check "%OUTDIR%\%~nx1\"
) else (
    echo Finished with ^(see messages above^)
)
pause
