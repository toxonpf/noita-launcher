# Build script for Noita Launcher (PowerShell)
# By default builds one-dir (folder) for easy debugging. Uncomment onefile line if needed.

$python = "C:/Program Files/Python313/python.exe"

# One-dir (recommended for debugging)
& $python -m PyInstaller --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py

# One-file (single exe) - uncomment to use
# & $python -m PyInstaller --onefile --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
