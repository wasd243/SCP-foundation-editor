@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Building Windows Executable...
pyinstaller --onefile --windowed --name="WikidotEditor" wikidot_edit_alpha_0.0.5.py

echo Build complete! Check the 'dist' folder.
pause
