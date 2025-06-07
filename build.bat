@echo off
echo ===========================================
echo  Building RDR2 Money Changer EXE
echo ===========================================

REM Building the app with PyInstaller 🚀
REM
REM --onefile bundles everything into a single exe 📦
REM --windowed for a clean GUI without console 🖥️
REM --upx-dir=. points to UPX compressor 🗜️
REM --icon sets our cool app icon 🎮
REM --name gives it the right name ✨
REM
REM Including our resources:
REM Background image and custom font 🎨

pyinstaller --onefile --windowed --upx-dir=. --icon="icon.ico" --name="RDR2 Money Changer" --add-data "res/bg.png;res" --add-data "res/chinese rocks.ttf;res" main.py

echo ===========================================
echo  Build process finished!
echo  Your file is in the 'dist' folder.
echo ===========================================
pause