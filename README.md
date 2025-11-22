# Noita Save Manager

Локальная утилита для управления слотами сохранений Noita.

Что включено

- `noita_launcher_gui.py` — основной GUI-скрипт (Tkinter).
- `config_gui.json` — packaged конфиг для первых запусков (копируется в `%APPDATA%/noita_launcher` при первом запуске).
- `logger.txt` — пример/файл для логов (опционально).

Быстрый старт (зависимости)

1. Установите Python 3.10+.
2. Установите зависимости:

```powershell
python -m pip install -r requirements.txt
```

Сборка в папку (рекомендовано для отладки)

```powershell
# запускает PyInstaller и кладёт результат в папку dist\noita_launcher_gui\
& "C:/Program Files/Python313/python.exe" -m PyInstaller --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```

Сборка в один .exe

```powershell
& "C:/Program Files/Python313/python.exe" -m PyInstaller --onefile --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```

Примечания

- При первом запуске упакованный `config_gui.json` копируется в `%APPDATA%/noita_launcher/config_gui.json` и далее используется оттуда.
- Для полноценной темы/кроссплатформенности можно использовать `ttkbootstrap`.

Как залить в репозиторий

1. Инициализируйте репозиторий (если ещё не инициализирован): `git init`.
2. Добавьте remote и запушьте: `git remote add origin <url>` и `git push -u origin main`.

Если хотите — укажите URL репозитория и я выполню `git remote add` + `git push` от вашего имени (нужен доступ).
