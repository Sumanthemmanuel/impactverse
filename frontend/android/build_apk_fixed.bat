@echo off
set "JAVA_HOME=c:\Users\Shanur\OneDrive\Desktop\Impactverse\github-repo\frontend\android\jdk21\jdk-21.0.2"
set "PATH=%JAVA_HOME%\bin;%PATH%"
echo Using JAVA_HOME: %JAVA_HOME%
java -version
call gradlew.bat assembleDebug
