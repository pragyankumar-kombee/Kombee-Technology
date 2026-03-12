@echo off
echo Setting up Git repository...

REM Remove existing .git folder
if exist .git rmdir /s /q .git

REM Create module-3 directory
if not exist module-3 mkdir module-3

REM Move all project files to module-3
move app.py module-3\
move train_bert.py module-3\
move inference.py module-3\
move test_sample.py module-3\
move requirements.txt module-3\
move .gitignore module-3\
xcopy /E /I /Y templates module-3\templates
xcopy /E /I /Y static module-3\static

REM Remove old directories
rmdir /s /q templates
rmdir /s /q static

REM Initialize new git repo
echo # Kombee-Technology >> README.md
git init
git add README.md
git add module-3
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/pragyankumar-kombee/Kombee-Technology.git
git push -u origin main --force

echo Done!
pause
