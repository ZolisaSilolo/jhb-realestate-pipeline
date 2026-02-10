@echo off
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot
set HADOOP_HOME=C:\Users\Lundi Zolisa Silolo\Data-Engineering-102\jhb-realestate-pipeline\hadoop
set PATH=%JAVA_HOME%\bin;%HADOOP_HOME%\bin;%PATH%
C:\Python312\python.exe src\analysis\generate_insights.py
