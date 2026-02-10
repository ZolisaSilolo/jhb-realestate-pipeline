@echo off
REM Export data for Fivetran ingestion

echo ========================================
echo Exporting Data for Fivetran
echo ========================================

set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot
set HADOOP_HOME=%~dp0hadoop
set PATH=%JAVA_HOME%\bin;%HADOOP_HOME%\bin;%PATH%

echo.
echo Running export script...
C:\Python312\python.exe src\export\prepare_for_fivetran.py

echo.
echo ========================================
echo Export Complete
echo ========================================
echo.
echo Next Steps:
echo 1. Upload files from exports/for_google_drive/ to Google Drive
echo 2. Configure Fivetran connector to sync from Google Drive to S3
echo 3. Run Databricks notebook to process data from S3
echo.
pause
