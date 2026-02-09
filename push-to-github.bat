@echo off
echo ========================================
echo Push Communication Bridge AI to GitHub
echo ========================================
echo.
echo STEP 1: Make sure you created the repository on GitHub first!
echo Go to: https://github.com/new
echo Repository name: communication-bridge-ai
echo.
pause
echo.
echo STEP 2: Adding GitHub remote...
git remote add origin https://github.com/Hlomohangcue/communication-bridge-ai.git
echo.
echo STEP 3: Verifying remote...
git remote -v
echo.
echo STEP 4: Pushing to GitHub...
echo You may be asked for credentials:
echo Username: Hlomohangcue
echo Password: Use your Personal Access Token (not your GitHub password)
echo.
git push -u origin master
echo.
echo ========================================
echo Done! Check your repository at:
echo https://github.com/Hlomohangcue/communication-bridge-ai
echo ========================================
pause
