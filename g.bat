@echo off
cls
echo GIT Command Line Interface
echo 1. [SAVE]  Add + Commit + Push
echo 2. [PULL]  Pull Changes from Remote
echo 3. [CHECK] Git Status
echo 4. [LOG]   View Recent History
echo 5. Exit
set /p choice="Select an Option (1-5): "
if "%choice%"=="1" goto save
if "%choice%"=="2" goto pull
if "%choice%"=="3" goto status
if "%choice%"=="4" goto log
if "%choice%"=="5" exit
exit
:save
echo.
echo STAGING ALL CHANGES 
git add .
echo.
set /p msg="Enter Commit Message (Press Enter for 'Auto Update'): "
if "%msg%"=="" set msg=Auto Update
echo.
echo COMMITTING 
git commit -m "%msg%"
echo.
echo PUSHING TO REMOTE 
git push
echo.
echo ✅ Done! Closing in 3 Seconds
timeout /t 3
exit
:pull
echo.
echo PULLING LATEST CHANGES 
git pull
echo.
echo ✅ Done! Closing in 3 Seconds
timeout /t 3
exit
:status
echo.
git status
echo.
echo Press Any Key to Close
pause
exit
:log
echo.
git log --oneline --graph --decorate -n 10
echo.
echo Press Any Key to Close
pause
exit