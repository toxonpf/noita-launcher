import json
import shutil
import subprocess
from threading import Thread
from pathlib import Path
from datetime import datetime
import sys
import os

import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog, ttk

# ---------- Конфиг ----------

# Определяем базовую папку в зависимости от режима (frozen при сборке PyInstaller)
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

# Ресурсный конфиг, который может быть упакован рядом с exe
PACKAGED_CONFIG = BASE_DIR / "config_gui.json"

# Путь для пользовательских данных (в Windows используем %APPDATA%)
USER_DATA_DIR = Path(os.getenv("APPDATA", Path.home())) / "noita_launcher"
USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Файл конфигурации, в который мы читаем/пишем (пользовательский)
CONFIG_FILE = USER_DATA_DIR / "config_gui.json"

if not CONFIG_FILE.exists() and PACKAGED_CONFIG.exists():
    try:
        shutil.copy2(PACKAGED_CONFIG, CONFIG_FILE)
    except Exception:
        pass


def load_config():
    default = {
        "noita_save_path": str(
            Path.home()
            / "AppData"
            / "LocalLow"
            / "Nolla_Games_Noita"
            / "save00"
        ),
        "noita_exe_path": r"C:\Games\Noita\noita.exe",
        "saves_dir": "saves",
        # Формат имени по умолчанию для слота (используется datetime.strftime)
        "save_name_format": "%Y-%m-%d_%H-%M-%S",
        # Тема интерфейса: 'light' или 'dark'
        "theme": "light",
        "language": "ru",
        # Подтверждать удаление слота
        "confirm_on_delete": True,
        # Авто-бэкап при запуске (пока заглушка, не используется)
        "auto_backup_on_run": False,
        "auto_backup_on_load": False,
        # Максимум бэкапов (интерактивно не реализовано сейчас)
        "max_backups": 0,
    }
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            default.update(data)
        except Exception:
            pass
    return default


def save_config(cfg):
    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


config = load_config()

NOITA_SAVE = Path(config["noita_save_path"])
NOITA_EXE = config["noita_exe_path"]
SAVES_DIR = Path(config["saves_dir"])
SAVES_DIR.mkdir(exist_ok=True)
TRANSLATIONS = {
    "ru": {
        "title": "Менеджер сохранений Noita",
        "subtitle": "Резервные копии save00 и быстрый выбор слотов для Noita.",
        "settings": "Настройки...",
        "browse": "Выбрать",
        "language": "Язык:",
        "save_path": "Путь к save00:",
        "exe_path": "Путь к Noita.exe:",
        "saves_dir": "Папка для слотов:",
        "open_logs": "Открыть журнал",
        "slots_label": "Слоты:",
        "rename_slot": "Переименовать",
        "delete_slot": "Удалить",
        "entry_label": "Имя для нового слота (опционально):",
        "save_btn": "Сохранить текущий прогресс",
        "load_btn": "Загрузить слот в save00",
        "overwrite_btn": "Перезаписать слот",
        "run_btn": "Запустить Noita с этим слотом",
        "warning": "Предупреждение",
        "confirm": "Подтверждение",
        "error": "Ошибка",
        "info": "Готово",
        "select_slot": "Сначала выберите слот в списке.",
        "save_missing": "Папка save00 не найдена:\n{path}",
        "slot_missing": "Слот не найден:\n{path}",
        "name_empty": "Имя не может быть пустым.",
        "backup_done": "Слот сохранен: {slot}",
        "load_done": "Слот \"{slot}\" восстановлен в save00.\nЗапустите Noita, чтобы продолжить.",
        "overwrite_confirm": "Перезаписать слот \"{slot}\" текущим save00? Старые файлы будут заменены.",
        "overwrite_done": "Слот \"{slot}\" обновлен.",
        "delete_confirm": "Удалить слот \"{slot}\"? Действие необратимо.",
        "rename_prompt": "Новое имя слота:",
        "rename_title": "Переименовать слот",
        "rename_exists": "Слот \"{slot}\" уже существует.",
        "log_title": "Журнал",
        "refresh": "Обновить",
        "close": "Закрыть",
        "noita_missing": "Noita.exe не найден:\n{path}\nУкажите путь в настройках.",
        "run_done": "Слот \"{slot}\" восстановлен. Noita запускается.",
        "auto_backup_fail": "Не удалось создать автокопию: {error}",
        "save00_label": "Путь к текущему save00:",
        "exe_label": "Путь к Noita.exe:",
        "saves_dir_label": "Каталог для слотов:",
        "format_label": "Шаблон имени слота (strftime):",
        "format_example": "Пример:",
        "theme_label": "Тема:",
        "language_label": "Язык:",
        "confirm_delete_label": "Спрашивать подтверждение перед удалением слотов",
        "auto_backup_run_label": "Автобэкап перед запуском Noita",
        "auto_backup_load_label": "Автобэкап перед загрузкой слота",
        "max_backups_label": "Максимум автокопий (0 = без лимита):",
        "reset_paths": "Сбросить пути по умолчанию",
        "reset_other": "Сбросить оформление и опции",
        "save_settings": "Сохранить",
        "cancel": "Отмена",
        "settings_saved": "Настройки сохранены.",
        "paths_header": "Пути",
        "list_header": "Слоты",
        "actions_header": "Действия",
        "status_idle": "Выберите слот или создайте новый.",
        "status_saved": "Создан слот {slot}.",
        "status_loaded": "Слот {slot} восстановлен.",
        "status_deleted": "Слот {slot} удален.",
        "status_renamed": "Слот переименован в {slot}.",
        "status_updated": "Слот {slot} обновлен.",
        "status_run": "Слот {slot} восстановлен, запуск Noita...",
    },
    "en": {
        "title": "Noita Save Manager",
        "subtitle": "Back up save00 and switch slots quickly for Noita.",
        "settings": "Settings...",
        "browse": "Browse",
        "language": "Language:",
        "save_path": "save00 path:",
        "exe_path": "Noita.exe path:",
        "saves_dir": "Slots folder:",
        "open_logs": "Open logs",
        "slots_label": "Slots:",
        "rename_slot": "Rename",
        "delete_slot": "Delete",
        "entry_label": "Name for a new slot (optional):",
        "save_btn": "Save current progress",
        "load_btn": "Load slot into save00",
        "overwrite_btn": "Overwrite slot",
        "run_btn": "Launch Noita with this slot",
        "warning": "Warning",
        "confirm": "Confirm",
        "error": "Error",
        "info": "Done",
        "select_slot": "Select a slot from the list first.",
        "save_missing": "save00 folder not found:\n{path}",
        "slot_missing": "Slot not found:\n{path}",
        "name_empty": "Name cannot be empty.",
        "backup_done": "Slot created: {slot}",
        "load_done": "Slot \"{slot}\" restored to save00. Start Noita to continue.",
        "overwrite_confirm": "Overwrite slot \"{slot}\" with current save00? Existing files will be replaced.",
        "overwrite_done": "Slot \"{slot}\" updated.",
        "delete_confirm": "Delete slot \"{slot}\"? This cannot be undone.",
        "rename_prompt": "New slot name:",
        "rename_title": "Rename slot",
        "rename_exists": "Slot \"{slot}\" already exists.",
        "log_title": "Logs",
        "refresh": "Refresh",
        "close": "Close",
        "noita_missing": "Noita.exe not found:\n{path}\nUpdate the path in settings.",
        "run_done": "Slot \"{slot}\" restored and Noita is launching.",
        "auto_backup_fail": "Auto-backup failed: {error}",
        "save00_label": "Path to current save00:",
        "exe_label": "Path to Noita.exe:",
        "saves_dir_label": "Directory for slots:",
        "format_label": "Slot name pattern (strftime):",
        "format_example": "Example:",
        "theme_label": "Theme:",
        "language_label": "Language:",
        "confirm_delete_label": "Ask before deleting slots",
        "auto_backup_run_label": "Auto-backup before launching Noita",
        "auto_backup_load_label": "Auto-backup before loading slot",
        "max_backups_label": "Max auto-backups (0 = unlimited):",
        "reset_paths": "Reset paths to default",
        "reset_other": "Reset look and options",
        "save_settings": "Save",
        "cancel": "Cancel",
        "settings_saved": "Settings saved.",
        "paths_header": "Paths",
        "list_header": "Slots",
        "actions_header": "Actions",
        "status_idle": "Pick a slot or create a new one.",
        "status_saved": "Slot {slot} created.",
        "status_loaded": "Slot {slot} restored.",
        "status_deleted": "Slot {slot} removed.",
        "status_renamed": "Slot renamed to {slot}.",
        "status_updated": "Slot {slot} updated.",
        "status_run": "Slot {slot} restored, launching Noita...",
        "status_saving": "Saving current save...",
        "status_loading": "Loading slot...",
        "status_overwrite": "Updating slot...",
        "status_running": "Preparing slot and launching...",
    },
}

def t(key: str) -> str:
    lang = config.get("language", "ru")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(
        key, TRANSLATIONS["en"].get(key, key)
    )




# ---------- Логика слотов ----------

def copy_dir(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

def cleanup_old_backups():
    max_b = int(config.get("max_backups", 0) or 0)
    if max_b <= 0 or not SAVES_DIR.exists():
        return
    dirs = [d for d in SAVES_DIR.iterdir() if d.is_dir()]
    if len(dirs) <= max_b:
        return
    dirs.sort(key=lambda d: d.stat().st_mtime)
    for d in dirs[:-max_b]:
        try:
            shutil.rmtree(d)
        except Exception:
            pass

def generate_auto_name(prefix: str) -> str:
    fmt = config.get("save_name_format", "%Y-%m-%d_%H-%M-%S")
    try:
        suffix = datetime.now().strftime(fmt)
    except Exception:
        suffix = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{prefix}{suffix}"


def make_backup(slot_name: str | None = None) -> str:
    """Сохранить текущий save00 в слот."""
    global NOITA_SAVE, SAVES_DIR

    if not NOITA_SAVE.exists():
        raise RuntimeError(t("save_missing").format(path=NOITA_SAVE))

    if not slot_name or slot_name.strip() == "":
        # используем формат из config (strftime)
        fmt = config.get("save_name_format", "%Y-%m-%d_%H-%M-%S")
        try:
            slot_name = datetime.now().strftime(fmt)
        except Exception:
            slot_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    dst = SAVES_DIR / slot_name
    copy_dir(NOITA_SAVE, dst)
    cleanup_old_backups()
    return slot_name


def load_slot(slot_name: str):
    global NOITA_SAVE, SAVES_DIR
    src = SAVES_DIR / slot_name
    if not src.exists():
        raise RuntimeError(f"Слот не найден:\n{src}")
    copy_dir(src, NOITA_SAVE)


# ---------- GUI ----------

class NoitaLauncherApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(t("title"))
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.option_add("*Font", ("Segoe UI", 10))
        self.option_add("*TButton.Padding", 8)
        self.option_add("*TCombobox.Padding", 6)
        self.status_var = tk.StringVar(value=t("status_idle"))
        # Разрешаем менять размер окна — это позволит прокрутке работать корректно
        self.resizable(True, True)

        self.create_widgets()
        # Применим тему из конфига сразу
        try:
            self.apply_theme(config.get("theme", "light"))
        except Exception:
            pass
        self.refresh_slots_list()

    def create_widgets(self):
        global config

        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill="both", expand=True)

        header = ttk.Frame(main_frame)
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, text=t("title"), style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text=t("subtitle"), wraplength=820, style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

        paths_frame = ttk.Labelframe(main_frame, text=t("paths_header"), padding=10)
        paths_frame.pack(fill="x", pady=(0, 10))

        save_row = ttk.Frame(paths_frame)
        save_row.pack(fill="x", pady=2)
        self.label_save_path = ttk.Label(
            save_row, text=f"{t('save00_label')} {config['noita_save_path']}", wraplength=760
        )
        self.label_save_path.pack(side="left", fill="x", expand=True)
        ttk.Button(save_row, text=t("browse"), width=10, command=self._choose_save_path).pack(side="right", padx=(8, 0))

        exe_row = ttk.Frame(paths_frame)
        exe_row.pack(fill="x", pady=2)
        self.label_exe_path = ttk.Label(
            exe_row, text=f"{t('exe_label')} {config['noita_exe_path']}", wraplength=760
        )
        self.label_exe_path.pack(side="left", fill="x", expand=True)
        ttk.Button(exe_row, text=t("browse"), width=10, command=self._choose_exe_path).pack(side="right", padx=(8, 0))

        saves_row = ttk.Frame(paths_frame)
        saves_row.pack(fill="x", pady=2)
        self.label_saves_dir = ttk.Label(
            saves_row, text=f"{t('saves_dir_label')} {config['saves_dir']}", wraplength=760
        )
        self.label_saves_dir.pack(side="left", fill="x", expand=True)
        ttk.Button(saves_row, text=t("browse"), width=10, command=self._choose_saves_dir).pack(side="right", padx=(8, 0))

        ttk.Button(paths_frame, text=t("settings"), command=self.open_settings_window).pack(anchor="e", pady=(6, 0))

        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)

        slots_section = ttk.Labelframe(content_frame, text=t("list_header"), padding=10)
        slots_section.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ttk.Label(slots_section, text=t("slots_label")).pack(anchor="w")
        list_container = ttk.Frame(slots_section)
        list_container.pack(fill="both", expand=True, pady=(4, 6))

        self.slots_listbox = tk.Listbox(list_container, height=14, activestyle="none", exportselection=False)
        self.slots_listbox.pack(side="left", fill="both", expand=True)
        vscroll = ttk.Scrollbar(list_container, orient="vertical", command=self.slots_listbox.yview)
        vscroll.pack(side="right", fill="y")
        self.slots_listbox.configure(yscrollcommand=vscroll.set)

        list_actions = ttk.Frame(slots_section)
        list_actions.pack(fill="x", pady=(2, 0))
        ttk.Button(list_actions, text=t("rename_slot"), command=self.on_rename_slot).pack(side="left", padx=(0, 6))
        ttk.Button(list_actions, text=t("delete_slot"), command=self.on_delete_slot).pack(side="left")

        actions_section = ttk.Labelframe(content_frame, text=t("actions_header"), padding=10)
        actions_section.pack(side="left", fill="both", expand=True)

        ttk.Label(actions_section, text=t("entry_label")).pack(anchor="w")
        self.slot_name_entry = ttk.Entry(actions_section)
        self.slot_name_entry.pack(fill="x", pady=(0, 6))

        primary_buttons = ttk.Frame(actions_section)
        primary_buttons.pack(fill="x", pady=(2, 0))
        ttk.Button(primary_buttons, text=t("save_btn"), command=self.on_save_current).pack(fill="x", pady=2)
        ttk.Button(primary_buttons, text=t("load_btn"), command=self.on_load_slot).pack(fill="x", pady=2)
        ttk.Button(primary_buttons, text=t("overwrite_btn"), command=self.on_overwrite_slot).pack(fill="x", pady=2)
        ttk.Button(primary_buttons, text=t("run_btn"), command=self.on_run_with_slot).pack(fill="x", pady=2)

        status_frame = ttk.Frame(self, padding=(8, 6))
        status_frame.pack(fill="x", side="bottom")
        ttk.Label(status_frame, textvariable=self.status_var, anchor="w", style="Status.TLabel").pack(
            side="left", fill="x", expand=True
        )
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=220)
        self.progress.pack(side="right", fill="x", padx=(8, 0))

    def _choose_save_path(self):
        """Выбор директории save00 через диалог выбора папки."""
        global config, NOITA_SAVE
        path = filedialog.askdirectory(title=t("save00_label"))
        if not path:
            return
        config["noita_save_path"] = path
        NOITA_SAVE = Path(path)
        save_config(config)
        self.label_save_path.config(text=f"{t('save00_label')} {path}")
        self.refresh_slots_list()

    def _choose_exe_path(self):
        """Выбор файла Noita.exe через диалог."""
        global config, NOITA_EXE
        path = filedialog.askopenfilename(
            title=t("exe_label"),
            filetypes=[("Noita", "*.exe"), ("All files", "*.*")]
        )
        if not path:
            return
        config["noita_exe_path"] = path
        NOITA_EXE = path
        save_config(config)
        self.label_exe_path.config(text=f"{t('exe_label')} {path}")

    def _choose_saves_dir(self):
        """Выбор каталога, в котором лежат пользовательские слоты."""
        global config, SAVES_DIR
        path = filedialog.askdirectory(title=t("saves_dir_label"))
        if not path:
            return
        config["saves_dir"] = path
        SAVES_DIR = Path(path)
        SAVES_DIR.mkdir(exist_ok=True)
        save_config(config)
        self.label_saves_dir.config(text=f"{t('saves_dir_label')} {path}")
        self.refresh_slots_list()


    # --- действия ---

    def set_status(self, key: str, slot: str | None = None):
        text = t(key)
        if slot:
            try:
                text = text.format(slot=slot)
            except Exception:
                pass
        self.status_var.set(text)

    def start_progress(self, key: str, slot: str | None = None):
        self.set_status(key, slot=slot)
        try:
            self.progress.configure(value=0, mode="indeterminate")
            self.progress.start(12)
        except Exception:
            pass
        self.update_idletasks()

    def stop_progress(self, key: str | None = None, slot: str | None = None):
        try:
            self.progress.stop()
            self.progress.configure(value=0)
        except Exception:
            pass
        if key:
            self.set_status(key, slot=slot)
        self.update_idletasks()

    def run_async(self, worker, *, on_success=None, on_error=None, final_status=None, slot=None):
        """Run blocking work in a thread so the progress bar animates."""

        def runner():
            try:
                result = worker()
            except Exception as exc:

                def handle_error():
                    if on_error:
                        on_error(exc)
                    else:
                        messagebox.showerror(t("error"), str(exc))
                    self.stop_progress("status_idle")

                self.after(0, handle_error)
                return

            def handle_success():
                if on_success:
                    on_success(result)
                self.stop_progress(final_status, slot=slot)

            self.after(0, handle_success)

        Thread(target=runner, daemon=True).start()

    # --- ???????? ---
    def get_selected_slot(self) -> str | None:
        sel = self.slots_listbox.curselection()
        if not sel:
            return None
        return self.slots_listbox.get(sel[0])

    def refresh_slots_list(self):
        global SAVES_DIR
        self.slots_listbox.delete(0, tk.END)
        if not SAVES_DIR.exists():
            SAVES_DIR.mkdir(exist_ok=True)
        slots = sorted(
            [d.name for d in SAVES_DIR.iterdir() if d.is_dir()]
        )
        for s in slots:
            self.slots_listbox.insert(tk.END, s)

    def on_save_current(self):
        name = self.slot_name_entry.get().strip() or None
        self.start_progress("status_saving", slot=name)

        def worker():
            return make_backup(name)

        def on_success(slot):
            self.slot_name_entry.delete(0, tk.END)
            self.refresh_slots_list()
            self.set_status("status_saved", slot)
            messagebox.showinfo(t("info"), t("backup_done").format(slot=slot))

        self.run_async(worker, on_success=on_success)

    def on_load_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning(t("warning"), t("select_slot"))
            return
        self.start_progress("status_loading", slot=slot)

        def worker():
            if config.get("auto_backup_on_load"):
                make_backup(generate_auto_name("auto_load_"))
            load_slot(slot)
            return slot

        def on_success(_):
            self.set_status("status_loaded", slot)
            messagebox.showinfo(t("info"), t("load_done").format(slot=slot))

        def on_error(err):
            messagebox.showerror(t("error"), str(err))

        self.run_async(worker, on_success=on_success, on_error=on_error)

    def on_overwrite_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning(t("warning"), t("select_slot"))
            return

        if not messagebox.askyesno(
            t("confirm"),
            t("overwrite_confirm").format(slot=slot),
        ):
            return

        self.start_progress("status_overwrite", slot=slot)

        def worker():
            make_backup(slot)
            return slot

        def on_success(_):
            self.refresh_slots_list()
            self.set_status("status_updated", slot)
            messagebox.showinfo(t("info"), t("overwrite_done").format(slot=slot))

        self.run_async(
            worker,
            on_success=on_success,
            on_error=lambda e: messagebox.showerror(t("error"), str(e)),
        )

    def on_delete_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning(t("warning"), t("select_slot"))
            return

        if config.get("confirm_on_delete", True):
            if not messagebox.askyesno(
                t("confirm"),
                t("delete_confirm").format(slot=slot),
            ):
                return

        try:
            target = SAVES_DIR / slot
            if target.exists():
                shutil.rmtree(target)
            self.refresh_slots_list()
            self.set_status("status_deleted", slot)
        except Exception as e:
            messagebox.showerror(t("error"), str(e))

    def on_rename_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning(t("warning"), t("select_slot"))
            return

        new_name = simpledialog.askstring(t("rename_title"), t("rename_prompt"), initialvalue=slot)
        if new_name is None:
            return

        new_name = new_name.strip()
        if new_name == "":
            messagebox.showwarning(t("warning"), t("name_empty"))
            return

        src = SAVES_DIR / slot
        dst = SAVES_DIR / new_name
        if dst.exists():
            messagebox.showerror(t("error"), t("rename_exists").format(slot=new_name))
            return

        try:
            src.rename(dst)
            self.refresh_slots_list()
            try:
                idx = list(sorted([d.name for d in SAVES_DIR.iterdir() if d.is_dir()])).index(new_name)
                self.slots_listbox.selection_clear(0, tk.END)
                self.slots_listbox.selection_set(idx)
                self.slots_listbox.see(idx)
            except Exception:
                pass
            self.set_status("status_renamed", new_name)
        except Exception as e:
            messagebox.showerror(t("error"), str(e))

    def open_logs_window(self):
        log_file = Path("logger.txt")

        win = tk.Toplevel(self)
        win.title(t("log_title"))
        win.geometry("760x520")
        win.minsize(520, 320)

        container = ttk.Frame(win)
        container.pack(fill="both", expand=True)
        container.rowconfigure(1, weight=1)
        container.columnconfigure(0, weight=1)

        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=0, column=0, sticky="we", padx=6, pady=6)

        text_frame = ttk.Frame(container)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        txt = tk.Text(text_frame, wrap="none", font=("Consolas", 10), undo=False)
        txt.grid(row=0, column=0, sticky="nsew")

        vscroll = ttk.Scrollbar(text_frame, orient="vertical", command=txt.yview)
        vscroll.grid(row=0, column=1, sticky="ns")
        hscroll = ttk.Scrollbar(text_frame, orient="horizontal", command=txt.xview)
        hscroll.grid(row=1, column=0, sticky="we")
        txt.configure(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        def _load_logs():
            txt.config(state="normal")
            txt.delete("1.0", tk.END)
            if log_file.exists():
                try:
                    txt.insert(tk.END, log_file.read_text(encoding="utf-8"))
                except Exception:
                    txt.insert(tk.END, "Could not read logger.txt.")
            else:
                txt.insert(tk.END, "logger.txt not found.")
            txt.config(state="disabled")

        ttk.Button(btn_frame, text=t("refresh"), command=_load_logs).pack(side="left", padx=4)
        ttk.Button(btn_frame, text=t("close"), command=win.destroy).pack(side="right", padx=4)

        self.apply_theme(config.get("theme", "light"), root_widget=win)
        _load_logs()

    def on_run_with_slot(self):
        global NOITA_EXE

        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning(t("warning"), t("select_slot"))
            return

        exe_path = Path(NOITA_EXE)
        if not exe_path.exists():
            messagebox.showerror(t("error"), t("noita_missing").format(path=exe_path))
            return

        self.start_progress("status_running", slot=slot)

        def worker():
            if config.get("auto_backup_on_run"):
                make_backup(generate_auto_name("auto_run_"))
            load_slot(slot)
            try:
                subprocess.Popen(
                    [str(exe_path)],
                    cwd=str(exe_path.parent),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as proc_err:
                raise RuntimeError(f"Failed to start Noita: {proc_err}")
            return slot

        def on_success(_):
            self.set_status("status_run", slot)
            messagebox.showinfo(t("info"), t("run_done").format(slot=slot))

        self.run_async(
            worker,
            on_success=on_success,
            on_error=lambda e: messagebox.showerror(t("error"), str(e)),
        )
    def open_settings_window(self):
        global config, NOITA_SAVE, NOITA_EXE, SAVES_DIR

        win = tk.Toplevel(self)
        win.title(t("settings"))
        win.geometry("720x560")
        win.resizable(True, True)

        frame = ttk.Frame(win, padding=12)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(1, weight=1)

        def browse_save():
            path = filedialog.askdirectory(title=t("save00_label"))
            if path:
                save_entry.delete(0, tk.END)
                save_entry.insert(0, path)

        def browse_exe():
            path = filedialog.askopenfilename(
                title=t("exe_label"),
                filetypes=[("Noita", "*.exe"), ("All files", "*.*")],
            )
            if path:
                exe_entry.delete(0, tk.END)
                exe_entry.insert(0, path)

        def browse_saves():
            path = filedialog.askdirectory(title=t("saves_dir_label"))
            if path:
                saves_entry.delete(0, tk.END)
                saves_entry.insert(0, path)

        row = 0
        ttk.Label(frame, text=t("save00_label")).grid(row=row, column=0, sticky="w")
        save_entry = ttk.Entry(frame)
        save_entry.grid(row=row + 1, column=0, columnspan=2, sticky="we", pady=(2, 8))
        save_entry.insert(0, config["noita_save_path"])
        ttk.Button(frame, text=t("browse"), command=browse_save).grid(row=row + 1, column=2, padx=(8, 0))

        row += 2
        ttk.Label(frame, text=t("exe_label")).grid(row=row, column=0, sticky="w")
        exe_entry = ttk.Entry(frame)
        exe_entry.grid(row=row + 1, column=0, columnspan=2, sticky="we", pady=(2, 8))
        exe_entry.insert(0, config["noita_exe_path"])
        ttk.Button(frame, text=t("browse"), command=browse_exe).grid(row=row + 1, column=2, padx=(8, 0))

        row += 2
        ttk.Label(frame, text=t("saves_dir_label")).grid(row=row, column=0, sticky="w")
        saves_entry = ttk.Entry(frame)
        saves_entry.grid(row=row + 1, column=0, columnspan=2, sticky="we", pady=(2, 8))
        saves_entry.insert(0, config["saves_dir"])
        ttk.Button(frame, text=t("browse"), command=browse_saves).grid(row=row + 1, column=2, padx=(8, 0))

        row += 2
        ttk.Label(frame, text=t("format_label")).grid(row=row, column=0, sticky="w")
        format_var = tk.StringVar(value=config.get("save_name_format", "%Y-%m-%d_%H-%M-%S"))
        format_entry = ttk.Entry(frame, textvariable=format_var)
        format_entry.grid(row=row + 1, column=0, sticky="we", pady=(2, 4))
        example_label = ttk.Label(frame, text=f"{t('format_example')} {datetime.now().strftime(format_var.get())}")
        example_label.grid(row=row + 1, column=1, columnspan=2, sticky="w", padx=(8, 0))

        row += 2
        ttk.Label(frame, text=t("theme_label")).grid(row=row, column=0, sticky="w", pady=(4, 0))
        theme_combo = ttk.Combobox(frame, values=["light", "dark"], state="readonly", width=10)
        theme_combo.grid(row=row, column=1, sticky="w", pady=(4, 0))
        theme_combo.set(config.get("theme", "light"))

        ttk.Label(frame, text=t("language_label")).grid(row=row, column=2, sticky="w", pady=(4, 0))
        lang_combo = ttk.Combobox(frame, values=["ru", "en"], state="readonly", width=6)
        lang_combo.grid(row=row + 1, column=2, sticky="w")
        lang_combo.set(config.get("language", "ru"))

        row += 2
        confirm_var = tk.BooleanVar(value=config.get("confirm_on_delete", True))
        auto_backup_var = tk.BooleanVar(value=config.get("auto_backup_on_run", False))
        auto_backup_load_var = tk.BooleanVar(value=config.get("auto_backup_on_load", False))

        ttk.Checkbutton(frame, text=t("confirm_delete_label"), variable=confirm_var).grid(row=row, column=0, columnspan=3, sticky="w", pady=(6, 2))
        ttk.Checkbutton(frame, text=t("auto_backup_run_label"), variable=auto_backup_var).grid(row=row + 1, column=0, columnspan=3, sticky="w")
        ttk.Checkbutton(frame, text=t("auto_backup_load_label"), variable=auto_backup_load_var).grid(row=row + 2, column=0, columnspan=3, sticky="w")

        row += 3
        ttk.Label(frame, text=t("max_backups_label")).grid(row=row, column=0, sticky="w", pady=(8, 2))
        max_backups_spin = ttk.Spinbox(frame, from_=0, to=1000, width=10)
        max_backups_spin.grid(row=row, column=1, sticky="w", pady=(8, 2))
        max_backups_spin.set(str(config.get("max_backups", 0)))

        row += 1
        ttk.Button(frame, text=t("open_logs"), command=self.open_logs_window).grid(row=row, column=0, sticky="w", pady=(8, 0))

        def _on_format_change(*_):
            try:
                example_label.config(text=f"{t('format_example')} {datetime.now().strftime(format_var.get())}")
            except Exception:
                example_label.config(text=t("format_example"))

        format_var.trace_add("write", _on_format_change)

        def _reset_paths():
            defaults = {
                "noita_save_path": str(Path.home() / "AppData" / "LocalLow" / "Nolla_Games_Noita" / "save00"),
                "noita_exe_path": r"C:\Games\Noita\noita.exe",
                "saves_dir": "saves",
            }
            save_entry.delete(0, tk.END)
            save_entry.insert(0, defaults["noita_save_path"])
            exe_entry.delete(0, tk.END)
            exe_entry.insert(0, defaults["noita_exe_path"])
            saves_entry.delete(0, tk.END)
            saves_entry.insert(0, defaults["saves_dir"])

        def _reset_other():
            format_var.set("%Y-%m-%d_%H-%M-%S")
            theme_combo.set("light")
            lang_combo.set("ru")
            confirm_var.set(True)
            auto_backup_var.set(False)
            auto_backup_load_var.set(False)
            max_backups_spin.set("0")
            self.apply_theme("light", root_widget=win)

        def save_settings():
            global config, NOITA_SAVE, NOITA_EXE, SAVES_DIR

            config["noita_save_path"] = save_entry.get().strip()
            config["noita_exe_path"] = exe_entry.get().strip()
            config["saves_dir"] = saves_entry.get().strip()
            config["save_name_format"] = format_var.get().strip() or "%Y-%m-%d_%H-%M-%S"
            config["theme"] = theme_combo.get()
            config["language"] = lang_combo.get()
            config["confirm_on_delete"] = bool(confirm_var.get())
            config["auto_backup_on_run"] = bool(auto_backup_var.get())
            config["auto_backup_on_load"] = bool(auto_backup_load_var.get())
            try:
                config["max_backups"] = int(max_backups_spin.get())
            except Exception:
                config["max_backups"] = 0

            NOITA_SAVE = Path(config["noita_save_path"])
            NOITA_EXE = config["noita_exe_path"]
            SAVES_DIR = Path(config["saves_dir"])
            SAVES_DIR.mkdir(exist_ok=True)

            save_config(config)

            self.label_save_path.config(text=f"{t('save00_label')} {config['noita_save_path']}")
            self.label_exe_path.config(text=f"{t('exe_label')} {config['noita_exe_path']}")
            self.label_saves_dir.config(text=f"{t('saves_dir_label')} {config['saves_dir']}")
            self.refresh_slots_list()

            try:
                self.apply_theme(config.get("theme", "light"))
                self.apply_theme(config.get("theme", "light"), root_widget=win)
            except Exception:
                pass

            self.title(t("title"))
            self.set_status("status_idle")

            messagebox.showinfo(t("info"), t("settings_saved"))
            win.destroy()

        bottom_btns = ttk.Frame(win, padding=(12, 0, 12, 12))
        bottom_btns.pack(fill="x", side="bottom")
        ttk.Button(bottom_btns, text=t("reset_paths"), command=_reset_paths).pack(side="left", padx=(0, 6))
        ttk.Button(bottom_btns, text=t("reset_other"), command=_reset_other).pack(side="left", padx=(0, 6))
        ttk.Button(bottom_btns, text=t("cancel"), command=win.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(bottom_btns, text=t("save_settings"), command=save_settings).pack(side="right")

        self.apply_theme(config.get("theme", "light"), root_widget=win)
    def apply_theme(self, theme_name: str, root_widget=None):
        """Apply a more complete light/dark theme to ttk and tk widgets."""
        target = root_widget or self
        style = ttk.Style(target)
        theme = theme_name or config.get("theme", "light")

        if theme == "dark":
            bg = "#0f1624"
            fg = "#e9efff"
            btn_bg = "#1c2537"
            entry_bg = "#1c2537"
            accent = "#2c3a55"
            disabled_fg = "#8d96a9"
        else:
            bg = "#f6f8fb"
            fg = "#10121a"
            btn_bg = "#e3e8f2"
            entry_bg = "#ffffff"
            accent = "#d5deef"
            disabled_fg = "#8a92a3"

        try:
            # Use a theme that respects custom colors
            try:
                style.theme_use("clam")
            except Exception:
                pass

            style.configure("TFrame", background=bg)
            style.configure("TLabel", background=bg, foreground=fg)
            style.configure("Title.TLabel", background=bg, foreground=fg, font=("Segoe UI Semibold", 16))
            style.configure("Subtitle.TLabel", background=bg, foreground=fg, font=("Segoe UI", 10))
            style.configure("Status.TLabel", background=accent, foreground=fg)
            style.configure("TButton", background=btn_bg, foreground=fg)
            style.configure("TCheckbutton", background=bg, foreground=fg)
            style.configure("TLabelframe", background=bg, foreground=fg)
            style.configure("TLabelframe.Label", background=bg, foreground=fg)
            style.configure("TScrollbar", background=btn_bg, troughcolor=bg)
            style.configure("Vertical.TScrollbar", background=btn_bg, troughcolor=bg)
            style.configure("Horizontal.TScrollbar", background=btn_bg, troughcolor=bg)

            style.configure("TEntry", fieldbackground=entry_bg, foreground=fg)
            style.configure("TCombobox", fieldbackground=entry_bg, foreground=fg)
            style.configure("TSpinbox", fieldbackground=entry_bg, foreground=fg)

            # Hover/active states
            style.map("TButton", background=[("active", accent), ("pressed", accent)])
            style.map(
                "TCombobox",
                fieldbackground=[("readonly", entry_bg)],
                foreground=[("disabled", disabled_fg)],
                background=[("readonly", btn_bg)],
            )
            style.map("TCheckbutton", foreground=[("disabled", disabled_fg)])

            try:
                target.configure(bg=bg)
            except Exception:
                pass

            # Walk widgets and adjust colors for Tk widgets that don't follow ttk styles
            def _recurse(widget):
                try:
                    widget.configure(bg=bg)
                except Exception:
                    pass

                for child in widget.winfo_children():
                    cls = child.winfo_class()
                    try:
                        if cls == "Text":
                            child.configure(
                                bg=entry_bg,
                                fg=fg,
                                insertbackground=fg,
                                selectbackground=accent,
                                selectforeground=fg,
                            )
                        elif cls == "Listbox":
                            child.configure(
                                bg=entry_bg,
                                fg=fg,
                                selectbackground=accent,
                                selectforeground=fg,
                            )
                        elif cls == "Canvas":
                            child.configure(bg=bg, highlightbackground=bg, highlightcolor=bg)
                        elif cls == "Button":
                            child.configure(bg=btn_bg, fg=fg, activebackground=accent)
                        elif cls == "Entry":
                            child.configure(bg=entry_bg, fg=fg, insertbackground=fg)
                    except Exception:
                        pass
                    _recurse(child)

            _recurse(target)
        except Exception:
            pass


if __name__ == "__main__":
    app = NoitaLauncherApp()
    app.mainloop()
