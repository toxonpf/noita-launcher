# Noita Save Manager

This README has English and Russian sections.

## English
### Overview
A Tkinter-based save manager for Noita. Backs up the `save00` folder, lets you switch save slots, and can launch Noita with the chosen slot. Settings live in `%APPDATA%/noita_launcher/config_gui.json`.

### Features
- Back up the current `save00` into a named slot (manual name or auto timestamp format).
- Load, overwrite, rename, and delete slots.
- Launch Noita with a selected slot (slot is copied to `save00` before start).
- Optional auto-backup before launching/loading, with `max_backups` limit for auto copies.
- Switch interface language (ru/en) and theme (light/dark).
- View `logger.txt` directly from the app.

### Requirements
- Windows, Python 3.10+.
- Dependencies from `requirements.txt` (PyInstaller only needed for building). `tkinter` ships with the standard library on Windows.

### Run from source
1) Install deps:
```
python -m pip install -r requirements.txt
```
2) Start the GUI:
```
python noita_launcher_gui.py
```
3) In `Settings`, set paths to `save00`, `Noita.exe`, and the slots directory (defaults to `saves` next to the app). You can also adjust theme, language, and slot name format.

### Usage
- **Save current run.** Enter a slot name (or leave empty for auto format) and click `Save current progress`.
- **Load / overwrite a slot.** Select a slot, then use `Load slot...` or `Overwrite slot`.
- **Launch the game.** Select a slot and click `Launch Noita with this slot` — the slot is copied into `save00`, then Noita starts.
- **Manage slots.** `Rename` and `Delete` buttons under the list. If `Confirm on delete` is enabled, a prompt appears before deletion.
- **Logs.** `Open logs` shows `logger.txt`.

### Configuration
`%APPDATA%/noita_launcher/config_gui.json` is created on first run from `config_gui.json`. Key fields:
- `noita_save_path` — path to current `save00` (e.g. `.../AppData/LocalLow/Nolla_Games_Noita/save00`).
- `noita_exe_path` — path to `Noita.exe`.
- `saves_dir` — directory for slots (default `saves` in working dir).
- `save_name_format` — slot name pattern (`strftime`), e.g. `%Y-%m-%d_%H-%M-%S`.
- `theme` — `light` or `dark`; `language` — `ru` or `en`.
- `confirm_on_delete` — ask before deleting slots.
- `auto_backup_on_run` / `auto_backup_on_load` — create auto backups (`auto_run_*` / `auto_load_*`) before launching or loading.
- `max_backups` — how many auto backups to keep (0 = unlimited).

### Project structure
- `noita_launcher_gui.py` — main Tkinter app.
- `config_gui.json` — settings template, copied to `%APPDATA%/noita_launcher` on first launch.
- `logger.txt` — app log, viewable via `Open logs`.
- `noita_launcher_gui.spec` — PyInstaller spec (adds `config_gui.json`, `logger.txt`, icon).
- `Spell_Swapper_projectile.ico` — icon for built exe.
- `build/`, `dist/`, `release/`, `saves/` — build artifacts and saved slots.

### Build exe (PyInstaller)
Install PyInstaller (`pip install -r requirements.txt`), then:
```powershell
python -m PyInstaller --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```
The exe will appear in `dist/noita_launcher_gui/`. One-file variant:
```powershell
python -m PyInstaller --onefile --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```
To add the icon, pass `--icon Spell_Swapper_projectile.ico` or use the provided `noita_launcher_gui.spec`.

### Troubleshooting
- `save00` not found — verify the path and permissions; create the folder if missing.
- `Noita.exe not found` — update the path in `Settings`.
- Antivirus flags the exe — add it to exclusions or build on a trusted machine.
- PyInstaller errors about paths — use a directory without spaces/non-ASCII characters.

### Notes
For releases you can init git, add a remote, and ship the built exe from `release/`.

---

## Русский
### Обзор
Менеджер сохранений для Noita на Tkinter. Делает резервные копии папки `save00`, позволяет быстро переключать слоты и запускать игру с выбранным сейвом. Настройки хранятся в `%APPDATA%/noita_launcher/config_gui.json`.

### Возможности
- Резервное копирование текущего `save00` в именованный слот (ручное имя или автоформат по дате).
- Загрузка, перезапись, переименование и удаление слотов.
- Запуск Noita с выбранным слотом (слот копируется в `save00` перед стартом).
- Автобэкап перед запуском/загрузкой, ограничение числа авто-копий через `max_backups`.
- Переключение языка интерфейса (ru/en) и темы (light/dark).
- Просмотр `logger.txt` прямо из приложения.

### Требования
- Windows, Python 3.10+.
- Зависимости из `requirements.txt` (PyInstaller нужен только для сборки). `tkinter` уже в стандартной библиотеке Windows.

### Запуск из исходников
1) Установите зависимости:
```
python -m pip install -r requirements.txt
```
2) Запустите GUI:
```
python noita_launcher_gui.py
```
3) В `Settings` задайте пути к `save00`, `Noita.exe` и каталогу слотов (по умолчанию `saves` рядом с приложением). Там же можно выбрать тему, язык и формат имени слота.

### Использование
- **Сохранить текущее прохождение.** Введите имя слота (или оставьте пустым для автоформата) и нажмите `Save current progress`.
- **Загрузить / перезаписать слот.** Выберите слот, затем `Load slot...` или `Overwrite slot`.
- **Запустить игру.** Выберите слот и нажмите `Launch Noita with this slot` — слот скопируется в `save00`, затем стартует Noita.
- **Управление слотами.** Кнопки `Rename` и `Delete` под списком. При включенной опции `Confirm on delete` будет запрос подтверждения.
- **Логи.** `Open logs` открывает `logger.txt`.

### Конфигурация
`%APPDATA%/noita_launcher/config_gui.json` создаётся при первом запуске из `config_gui.json`. Основные поля:
- `noita_save_path` — путь к текущей папке `save00` (пример: `.../AppData/LocalLow/Nolla_Games_Noita/save00`).
- `noita_exe_path` — путь к `Noita.exe`.
- `saves_dir` — папка со слотами (по умолчанию `saves` в рабочем каталоге).
- `save_name_format` — шаблон имени слота (`strftime`), например `%Y-%m-%d_%H-%M-%S`.
- `theme` — `light` или `dark`; `language` — `ru` или `en`.
- `confirm_on_delete` — спрашивать подтверждение перед удалением слотов.
- `auto_backup_on_run` / `auto_backup_on_load` — делать авто-бэкап (`auto_run_*` / `auto_load_*`) перед запуском или загрузкой слота.
- `max_backups` — сколько авто-бэкапов хранить (0 — без ограничения).

### Структура проекта
- `noita_launcher_gui.py` — основное приложение Tkinter.
- `config_gui.json` — шаблон настроек, копируется в `%APPDATA%/noita_launcher` при первом запуске.
- `logger.txt` — лог приложения, доступен через `Open logs`.
- `noita_launcher_gui.spec` — конфиг сборки PyInstaller (добавляет `config_gui.json`, `logger.txt`, иконку).
- `Spell_Swapper_projectile.ico` — иконка для собранного exe.
- `build/`, `dist/`, `release/`, `saves/` — артефакты сборки и сохранения слотов.

### Сборка exe (PyInstaller)
Убедитесь, что PyInstaller установлен (`pip install -r requirements.txt`), затем:
```powershell
python -m PyInstaller --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```
Готовый exe появится в `dist/noita_launcher_gui/`. Однофайловый вариант:
```powershell
python -m PyInstaller --onefile --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```
Чтобы добавить иконку, укажите `--icon Spell_Swapper_projectile.ico` или используйте `noita_launcher_gui.spec`.

### Частые проблемы
- Сообщение `save00` not found — проверьте путь и права, при необходимости создайте папку.
- Ошибка `Noita.exe not found` — обновите путь в `Settings`.
- Антивирус может блокировать собранный exe; добавьте его в исключения или собирайте на доверенной машине.
- Ошибки PyInstaller из-за путей — используйте каталог без пробелов и кириллицы.

### Заметки
Для релизов можно инициализировать git, добавить удалённый репозиторий и выкладывать собранный exe в `release/`.
