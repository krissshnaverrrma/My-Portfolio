@echo off
cls
echo  GIT Command Line Interface
echo 1. [SAVE]  Add + Commit + Push
echo 2. [PULL]  Pull Changes from Remote
echo 3. [CHECK]  Git Status
echo 4. [LOG]  View Recent History
echo 5. [BRANCH]  List All Branches
echo 6. [SWITCH]  Switch or Create Branch
echo 7. [STASH]  Stash Uncommitted Changes
echo 8. [DISCARD]  Discard All Local Changes
echo 9. Exit
set /p choice="Select an Option (1-9): "

if "%choice%"=="1" goto save
if "%choice%"=="2" goto pull
if "%choice%"=="3" goto status
if "%choice%"=="4" goto log
if "%choice%"=="5" goto branch
if "%choice%"=="6" goto switch
if "%choice%"=="7" goto stash
if "%choice%"=="8" goto discard
if "%choice%"=="9" exit
exit

:save
echo.
echo STAGING ALL CHANGES...
git add .
echo.
set /p msg="Enter Commit Message (Press Enter for 'Auto Update'): "
if "%msg%"=="" set msg=Auto Update
echo.
echo COMMITTING...
git commit -m "%msg%"
echo.
echo PUSHING TO REMOTE...
git push
echo.
echo ✅ Done! Closing in 3 Seconds...
timeout /t 3 >nul
exit

:pull
echo.
echo PULLING LATEST CHANGES...
git pull
echo.
echo ✅ Done! Closing in 3 Seconds...
timeout /t 3 >nul
exit

:status
echo.
echo CURRENT REPOSITORY STATUS:
git status
echo.
echo Press Any Key to Return to Menu...
pause >nul
goto restart

:log
echo.
echo RECENT COMMIT HISTORY:
git log --oneline --graph --decorate -n 10
echo.
echo Press Any Key to Return to Menu...
pause >nul
goto restart

:branch
echo.
echo LOCAL AND REMOTE BRANCHES:
git branch -a
echo.
echo Press Any Key to Return to Menu...
pause >nul
goto restart

:switch
echo.
echo CURRENT BRANCH:
git branch --show-current
echo.
set /p bname="Enter Branch Name to Switch to (or create new): "
if "%bname%"=="" goto restart
echo.
echo SWITCHING...
git checkout -B "%bname%"
echo.
echo Press Any Key to Return to Menu...
pause >nul
goto restart

:stash
echo.
echo STASHING UNCOMMITTED CHANGES...
git stash
echo.
echo ✅ Done! Press Any Key to Return to Menu...
pause >nul
goto restart

:discard
echo.
echo ⚠️  WARNING: This will permanently delete all uncommitted changes!
set /p confirm="Are you sure you want to discard changes? (Y/N): "
if /i "%confirm%"=="Y" (
  echo.
  echo DISCARDING CHANGES...
  git restore .
  git clean -fd
  echo ✅ Local changes discarded!
  ) else (
  echo.
  echo ❌ Aborted. No changes were deleted.
)
echo.
echo Press Any Key to Return to Menu...
pause >nul
goto restart

:restart
cls
%0
