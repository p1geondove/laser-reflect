# Compiles the project to windows .exe
# sometimes the icon doesnt show up, but thats a windows cahing issue wich can be resolved by just moving the .exe
# https://github.com/pyinstaller/pyinstaller/issues/8784

$MAIN_DIR = "C:\Users\p1geon\Documents\code\laser-reflect"  # change this path
$MAIN_FILE = Join-Path $MAIN_DIR "main.py"
$SCRIPTS_DIR = Join-Path $MAIN_DIR "scripts"

# PyInstaller command (same flags, Windows-compatible paths)
pyinstaller --onefile --windowed `
    --add-data "$SCRIPTS_DIR;scripts" `
    $MAIN_FILE