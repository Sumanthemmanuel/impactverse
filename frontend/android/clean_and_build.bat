@echo off
set "JAVA_HOME=c:\Users\Shanur\OneDrive\Desktop\Impactverse\github-repo\frontend\android\jdk21\jdk-21.0.2"
set "PATH=%JAVA_HOME%\bin;%PATH%"
call gradlew.bat --stop
rmdir /s /q build
rmdir /s /q app\build
call build_apk_fixed.bat
