# Noita Save Manager

Менеджер сохранений для Noita на Tkinter. Делает резервные копии папки `save00`, позволяет быстро переключать слоты и запускать игру с выбранным сейвом. Настройки сохраняются в `%APPDATA%/noita_launcher/config_gui.json`.

## Возможности
- резервное копирование текущего `save00` в именованный слот (ручное имя или автоформат по дате);
- загрузка, перезапись, переименование и удаление слотов;
- запуск Noita с выбранным слотом (перед запуском слот копируется в `save00`);
- автоматический бэкап перед запуском/загрузкой слота, ограничение числа автокопий (`max_backups`);
- переключение языка интерфейса (ru/en) и темы (light/dark);
- просмотр файла `logger.txt` прямо из приложения.

## Требования
- Windows, Python 3.10+;
- зависимости из `requirements.txt` (PyInstaller нужен только для сборки), `tkinter` есть в стандартной библиотеке.

## Запуск из исходников
1. Установите зависимости:  
   `python -m pip install -r requirements.txt`
2. Запустите GUI:  
   `python noita_launcher_gui.py`
3. В окне `Settings` укажите пути к `save00`, `Noita.exe` и каталогу со слотами (по умолчанию `saves` рядом с программой), настройте тему, язык и формат имени слота.

## Использование
- **Сохранить текущее прохождение.** Введите имя слота (или оставьте пустым для автоформата) и нажмите `Save current progress`.
- **Загрузить / перезаписать слот.** Выберите слот в списке и нажмите `Load slot...` или `Overwrite slot`.
- **Запустить игру.** Выберите слот и нажмите `Launch Noita with this slot` — слот загрузится в `save00`, затем запустится Noita.
- **Управление слотами.** Кнопки `Rename` и `Delete` под списком. При включенной настройке `Confirm on delete` будет запрашиваться подтверждение.
- **Логи.** Кнопка `Open logs` открывает `logger.txt`.

## Конфигурация
Файл `%APPDATA%/noita_launcher/config_gui.json` создаётся автоматически из `config_gui.json`. Основные поля:
- `noita_save_path` — путь к текущей папке `save00` (`.../AppData/LocalLow/Nolla_Games_Noita/save00`);
- `noita_exe_path` — путь к `Noita.exe`;
- `saves_dir` — папка со слотами (по умолчанию `saves` в рабочем каталоге);
- `save_name_format` — шаблон имени слота (`strftime`), например `%Y-%m-%d_%H-%M-%S`;
- `theme` — `light` или `dark`; `language` — `ru` или `en`;
- `confirm_on_delete` — спрашивать подтверждение перед удалением;
- `auto_backup_on_run` / `auto_backup_on_load` — делать авто-бэкап (`auto_run_*`/`auto_load_*`) перед запуском или загрузкой слота;
- `max_backups` — сколько авто-бэкапов хранить (0 — без ограничения).

## Структура
- `noita_launcher_gui.py` — основное приложение Tkinter.
- `config_gui.json` — шаблон настроек, копируется в `%APPDATA%/noita_launcher` при первом запуске.
- `logger.txt` — лог работы приложения, доступен через кнопку `Open logs`.
- `noita_launcher_gui.spec` — конфиг сборки PyInstaller (добавляет `config_gui.json`, `logger.txt`, иконку).
- `Spell_Swapper_projectile.ico` — иконка для собранного exe.
- `build/`, `dist/`, `release/`, `saves/` — артефакты сборки и сохранения слотов.

## Сборка exe (PyInstaller)
Убедитесь, что PyInstaller установлен (`pip install -r requirements.txt`), затем:
```powershell
python -m PyInstaller --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```
Готовый exe появится в `dist/noita_launcher_gui/`. Однофайловый вариант:
```powershell
python -m PyInstaller --onefile --windowed --add-data "config_gui.json;." --add-data "logger.txt;." noita_launcher_gui.py
```
Для кастомной иконки добавьте `--icon Spell_Swapper_projectile.ico` или используйте готовый `noita_launcher_gui.spec`.

## Частые проблемы
- Сообщение о том, что `save00` не найден — проверьте путь и права доступа, при необходимости создайте папку.
- Ошибка `Noita.exe not found` — обновите путь в `Settings`.
- Антивирус может блокировать собранный exe; добавьте его в исключения или собирайте на машине с доверенным сертификатом.
- Если сборка PyInstaller падает из-за путей, используйте каталог без пробелов и кириллицы.

## Разработка
Для коммитов и релизов можно инициализировать git, добавить удалённый репозиторий и выкатывать собранный exe в `release/`.
