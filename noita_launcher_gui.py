import json
import shutil
import subprocess
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
        "settings": "?????????...",
        "language": "???? ??????????:",
        "save_path": "???? ? save00:",
        "exe_path": "???? ? Noita.exe:",
        "saves_dir": "????? ??? ??????:",
        "open_logs": "??????? ????",
    },
    "en": {
        "settings": "Settings...",
        "language": "Language:",
        "save_path": "save00 path:",
        "exe_path": "Noita.exe path:",
        "saves_dir": "Slots folder:",
        "open_logs": "Open logs",
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
        raise RuntimeError(f"Папка save00 не найдена:\n{NOITA_SAVE}")

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

        self.title("Noita Save Manager")
        self.geometry("800x600")
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

        # Создадим основной фрейм: сверху будет прокручиваемая область с контентом,
        # внизу — фиксированная панель с полем имени и кнопками.
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Canvas + вертикальная полоса прокрутки для контента
        canvas = tk.Canvas(main_frame, borderwidth=0, highlightthickness=0)
        vscroll = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)

        vscroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content_frame = ttk.Frame(canvas)
        # Вставляем фрейм в canvas
        self._canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Обновлять область прокрутки при изменении размера контента
        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        content_frame.bind("<Configure>", _on_frame_configure)

        # Поддержка изменения ширины: подгонять содержимое под ширину canvas
        def _on_canvas_configure(event):
            canvas.itemconfigure(self._canvas_window, width=event.width)

        canvas.bind("<Configure>", _on_canvas_configure)

        # Верхняя панель с путями (внутри прокручиваемой области)
        top_frame = ttk.Frame(content_frame)
        top_frame.pack(fill="x", padx=10, pady=5)
        save_row = ttk.Frame(top_frame)
        save_row.pack(fill="x", anchor="w")
        self.label_save_path = ttk.Label(save_row, text=f"save00: {config['noita_save_path']}" , wraplength=480)
        self.label_save_path.pack(side="left", anchor="w", expand=True, fill="x")
        ttk.Button(save_row, text="Browse", width=8, command=self._choose_save_path).pack(side="right", padx=(6, 0))

        exe_row = ttk.Frame(top_frame)
        exe_row.pack(fill="x", anchor="w", pady=(2, 5))
        self.label_exe_path = ttk.Label(exe_row, text=f"Noita.exe: {config['noita_exe_path']}" , wraplength=480)
        self.label_exe_path.pack(side="left", anchor="w", expand=True, fill="x")
        ttk.Button(exe_row, text="Browse", width=8, command=self._choose_exe_path).pack(side="right", padx=(6, 0))

        settings_btn = ttk.Button(
            top_frame,
            text="Настройки...",
            command=self.open_settings_window
        )
        settings_btn.pack(anchor="e")

        # Список слотов (тоже внутри прокручиваемой области)
        middle_frame = ttk.Frame(content_frame)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        ttk.Label(middle_frame, text="Слоты:").pack(anchor="w")

        self.slots_listbox = tk.Listbox(middle_frame, height=10)
        self.slots_listbox.pack(fill="both", expand=True, pady=5)

        # Кнопки действия над списком: переименовать и удалить слот
        list_actions = ttk.Frame(middle_frame)
        list_actions.pack(fill="x", pady=(4, 0))

        rename_btn = ttk.Button(list_actions, text="Переименовать слот", command=self.on_rename_slot)
        rename_btn.pack(side="left", padx=(0, 6))

        delete_btn = ttk.Button(list_actions, text="Удалить слот", command=self.on_delete_slot)
        delete_btn.pack(side="left")

        # Фиксированная нижняя панель с именем слота и кнопками — всегда видна
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", side="bottom", padx=10, pady=5)

        ttk.Label(bottom_frame, text="Имя нового слота (опционально):").grid(
            row=0, column=0, columnspan=3, sticky="w"
        )

        self.slot_name_entry = ttk.Entry(bottom_frame)
        self.slot_name_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=2)

        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(2, weight=1)

        # Кнопки действий — используем tk.Button с поддержкой переноса текста
        # начальный wraplength будет установлен при изменении размера панели
        save_btn = tk.Button(
            bottom_frame,
            text="Сохранить текущий прогресс",
            command=self.on_save_current,
            wraplength=150,
            justify="center",
        )
        save_btn.grid(row=2, column=0, columnspan=3, sticky="we", pady=(5, 5))

        load_btn = tk.Button(
            bottom_frame,
            text="Загрузить выбранный слот",
            command=self.on_load_slot,
            wraplength=150,
            justify="center",
        )
        load_btn.grid(row=3, column=0, sticky="we", pady=2)

        overwrite_btn = tk.Button(
            bottom_frame,
            text="Перезаписать слот",
            command=self.on_overwrite_slot,
            wraplength=150,
            justify="center",
        )
        overwrite_btn.grid(row=3, column=1, sticky="we", pady=2)

        run_btn = tk.Button(
            bottom_frame,
            text="Запустить Noita с этим слотом",
            command=self.on_run_with_slot,
            wraplength=150,
            justify="center",
        )
        run_btn.grid(row=3, column=2, sticky="we", pady=2)

        # Динамически подстраиваем wraplength кнопок под текущую ширину панели
        def _update_button_wrap(event):
            try:
                total_width = event.width
                # отнимем небольшие отступы и разделим на 3 колонки
                per_col = max(50, (total_width - 20) // 3)
                wrap = per_col - 10
                save_btn.configure(wraplength=wrap)
                load_btn.configure(wraplength=wrap)
                overwrite_btn.configure(wraplength=wrap)
                run_btn.configure(wraplength=wrap)
            except Exception:
                pass

        bottom_frame.bind("<Configure>", _update_button_wrap)

    def _choose_save_path(self):
        """??????? ????? save00 ?? ????????? ???? ? ????? ????????? ??????."""
        global config, NOITA_SAVE
        path = filedialog.askdirectory(title="???????? ?????????? save00")
        if not path:
            return
        config["noita_save_path"] = path
        NOITA_SAVE = Path(path)
        save_config(config)
        self.label_save_path.config(text=f"save00: {path}")
        self.refresh_slots_list()

    def _choose_exe_path(self):
        """??????? ???? Noita.exe ?? ????????? ???? ? ????? ????????? ??????."""
        global config, NOITA_EXE
        path = filedialog.askopenfilename(
            title="???????? Noita.exe",
            filetypes=[("Noita", "*.exe"), ("??? ?????", "*.*")]
        )
        if not path:
            return
        config["noita_exe_path"] = path
        NOITA_EXE = path
        save_config(config)
        self.label_exe_path.config(text=f"Noita.exe: {path}")


    # --- действия ---

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
        name = self.slot_name_entry.get().strip()
        try:
            slot = make_backup(name)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
        self.slot_name_entry.delete(0, tk.END)
        self.refresh_slots_list()
        messagebox.showinfo("Готово", f"Слот сохранён: {slot}")

    def on_load_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning("Warning", "Select a slot from the list first.")
        if config.get("auto_backup_on_load"):
            try:
                make_backup(generate_auto_name("auto_load_"))
            except Exception as e:
                messagebox.showerror("Error", f"Auto-backup failed before loading: {e}")
        try:
            load_slot(slot)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        messagebox.showinfo("Done", f"Slot '{slot}' restored to save00.\nStart Noita to continue.")

    def on_overwrite_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning("Warning", "Select a slot from the list first.")
            return

        if not messagebox.askyesno(
            "Confirm",
            f"Overwrite slot '{slot}' with current save00?\n(existing files will be replaced)",
        ):
            return

        try:
            make_backup(slot)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        self.refresh_slots_list()
        messagebox.showinfo("Done", f"Slot '{slot}' updated.")

    def on_delete_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning("Warning", "Select a slot from the list first.")
            return

        if config.get("confirm_on_delete", True):
            if not messagebox.askyesno(
                "Confirm",
                f"Delete slot '{slot}'? This cannot be undone.",
            ):
                return

        try:
            target = SAVES_DIR / slot
            if target.exists():
                shutil.rmtree(target)
            self.refresh_slots_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_rename_slot(self):
        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning("Warning", "Select a slot from the list first.")
            return

        new_name = simpledialog.askstring("Rename slot", "New slot name:", initialvalue=slot)
        if new_name is None:
            return

        new_name = new_name.strip()
        if new_name == "":
            messagebox.showwarning("Warning", "Name cannot be empty.")
            return

        src = SAVES_DIR / slot
        dst = SAVES_DIR / new_name
        if dst.exists():
            messagebox.showerror("Error", f"Slot '{new_name}' already exists.")
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
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_logs_window(self):
        log_file = Path("logger.txt")

        win = tk.Toplevel(self)
        win.title("Logs")
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

        ttk.Button(btn_frame, text="Refresh", command=_load_logs).pack(side="left", padx=4)
        ttk.Button(btn_frame, text="Close", command=win.destroy).pack(side="right", padx=4)

        self.apply_theme(config.get("theme", "light"), root_widget=win)
        _load_logs()

    def on_run_with_slot(self):
        global NOITA_EXE

        slot = self.get_selected_slot()
        if not slot:
            messagebox.showwarning("Warning", "Select a slot from the list first.")
            return

        exe_path = Path(NOITA_EXE)
        if not exe_path.exists():
            messagebox.showerror("Error", f"Noita.exe not found:\n{exe_path}\nUpdate the path in settings.")
            return

        if config.get("auto_backup_on_run"):
            try:
                make_backup(generate_auto_name("auto_run_"))
            except Exception as e:
                messagebox.showerror("Error", f"Auto-backup failed before launching: {e}")
                return

        try:
            load_slot(slot)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            subprocess.Popen(
                [str(exe_path)],
                cwd=str(exe_path.parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start Noita: {e}")
            return

        messagebox.showinfo("Run", f"Slot '{slot}' restored and Noita is launching.")

    def open_settings_window(self):
        global config, NOITA_SAVE, NOITA_EXE, SAVES_DIR

        win = tk.Toplevel(self)
        win.title("Настройки")
        win.geometry("640x360")
        win.resizable(True, True)

        # Сделаем прокручиваемую область для настроек (вертикальный скролл)
        settings_canvas = tk.Canvas(win, borderwidth=0, highlightthickness=0)
        settings_vscroll = ttk.Scrollbar(win, orient="vertical", command=settings_canvas.yview)
        settings_canvas.configure(yscrollcommand=settings_vscroll.set)
        settings_vscroll.pack(side="right", fill="y")
        settings_canvas.pack(side="left", fill="both", expand=True)

        settings_frame = ttk.Frame(settings_canvas)
        settings_window = settings_canvas.create_window((0, 0), window=settings_frame, anchor="nw")

        def _on_settings_configure(event):
            settings_canvas.configure(scrollregion=settings_canvas.bbox("all"))

        settings_frame.bind("<Configure>", _on_settings_configure)

        def _on_settings_canvas_configure(event):
            settings_canvas.itemconfigure(settings_window, width=event.width)

        settings_canvas.bind("<Configure>", _on_settings_canvas_configure)

        # пути
        ttk.Label(settings_frame, text="Путь к папке save00:").grid(
            row=0, column=0, sticky="w", padx=10, pady=(10, 2)
        )
        save_entry = ttk.Entry(settings_frame, width=60)
        save_entry.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        save_entry.insert(0, config["noita_save_path"])

        def browse_save():
            path = filedialog.askdirectory(title="Выбери папку save00")
            if path:
                save_entry.delete(0, tk.END)
                save_entry.insert(0, path)

        ttk.Button(settings_frame, text="Обзор...", command=browse_save).grid(
            row=1, column=1, padx=5, pady=2
        )

        ttk.Label(settings_frame, text="Путь к Noita.exe:").grid(
            row=2, column=0, sticky="w", padx=10, pady=(10, 2)
        )
        exe_entry = ttk.Entry(settings_frame, width=60)
        exe_entry.grid(row=3, column=0, padx=10, pady=2, sticky="w")
        exe_entry.insert(0, config["noita_exe_path"])

        def browse_exe():
            path = filedialog.askopenfilename(
                title="Выбери Noita.exe",
                filetypes=[("Noita", "*.exe"), ("Все файлы", "*.*")]
            )
            if path:
                exe_entry.delete(0, tk.END)
                exe_entry.insert(0, path)

        ttk.Button(settings_frame, text="Обзор...", command=browse_exe).grid(
            row=3, column=1, padx=5, pady=2
        )

        ttk.Label(settings_frame, text="Папка для слотов:").grid(
            row=4, column=0, sticky="w", padx=10, pady=(10, 2)
        )
        saves_entry = ttk.Entry(settings_frame, width=60)
        saves_entry.grid(row=5, column=0, padx=10, pady=2, sticky="w")
        saves_entry.insert(0, config["saves_dir"])

        def browse_saves():
            path = filedialog.askdirectory(title="Выбери папку для слотов")
            if path:
                saves_entry.delete(0, tk.END)
                saves_entry.insert(0, path)

        ttk.Button(settings_frame, text="Обзор...", command=browse_saves).grid(
            row=5, column=1, padx=5, pady=2
        )

        # Формат имени слота
        ttk.Label(settings_frame, text="Формат имени слота (strftime):").grid(
            row=6, column=0, sticky="w", padx=10, pady=(10, 2)
        )
        format_entry = ttk.Entry(settings_frame, width=60)
        format_entry.grid(row=7, column=0, padx=10, pady=2, sticky="w")
        format_entry.insert(0, config.get("save_name_format", "%Y-%m-%d_%H-%M-%S"))

        ttk.Label(settings_frame, text="Пример:").grid(row=7, column=1, sticky="w")
        example_label = ttk.Label(settings_frame, text=datetime.now().strftime(config.get("save_name_format", "%Y-%m-%d_%H-%M-%S")))
        example_label.grid(row=7, column=2, sticky="w", padx=5)

        # Тема
        ttk.Label(settings_frame, text="Тема интерфейса:").grid(
            row=8, column=0, sticky="w", padx=10, pady=(10, 2)
        )
        theme_combo = ttk.Combobox(settings_frame, values=["light", "dark"], state="readonly", width=10)
        theme_combo.grid(row=9, column=0, sticky="w", padx=10, pady=2)
        theme_combo.set(config.get("theme", "light"))

        # Язык интерфейса
        ttk.Label(settings_frame, text="Language:").grid(
            row=8, column=1, sticky="w", padx=10, pady=(10, 2)
        )
        lang_combo = ttk.Combobox(settings_frame, values=["ru", "en"], state="readonly", width=6)
        lang_combo.grid(row=9, column=1, sticky="w", padx=10, pady=2)
        lang_combo.set(config.get("language", "ru"))

        # Settings behavior
        confirm_var = tk.BooleanVar(value=config.get("confirm_on_delete", True))
        ttk.Checkbutton(settings_frame, text="Confirm before deleting slots", variable=confirm_var).grid(row=10, column=0, sticky="w", padx=10, pady=2)

        auto_backup_var = tk.BooleanVar(value=config.get("auto_backup_on_run", False))
        ttk.Checkbutton(settings_frame, text="Auto-backup before launching Noita (selected slot)", variable=auto_backup_var).grid(row=11, column=0, sticky="w", padx=10, pady=2)
        auto_backup_load_var = tk.BooleanVar(value=config.get("auto_backup_on_load", False))
        ttk.Checkbutton(settings_frame, text="Auto-backup before loading slot into save00", variable=auto_backup_load_var).grid(row=12, column=0, sticky="w", padx=10, pady=2)

        ttk.Label(settings_frame, text="Max backups (0 = unlimited):").grid(row=13, column=0, sticky="w", padx=10, pady=(10, 2))
        max_backups_spin = ttk.Spinbox(settings_frame, from_=0, to=1000, width=8)
        max_backups_spin.grid(row=13, column=1, sticky="w", padx=10, pady=2)
        max_backups_spin.set(str(config.get("max_backups", 0)))

        # Кнопка открытия логов
        ttk.Button(settings_frame, text="Open logs", command=self.open_logs_window).grid(row=14, column=0, sticky="w", padx=10, pady=8)

        # Обновление примера формата при изменении
        def _on_format_change(*args):
            try:
                example_label.config(text=datetime.now().strftime(format_var.get()))
            except Exception:
                example_label.config(text="Неверный формат")

        format_var = tk.StringVar(value=config.get("save_name_format", "%Y-%m-%d_%H-%M-%S"))
        format_entry.config(textvariable=format_var)
        format_var.trace_add("write", _on_format_change)

        # Превью темы при выборе
        def _on_theme_change(event):
            try:
                self.apply_theme(theme_combo.get())
            except Exception:
                pass

        theme_combo.bind('<<ComboboxSelected>>', _on_theme_change)

        def save_settings():
            global config, NOITA_SAVE, NOITA_EXE, SAVES_DIR

            config["noita_save_path"] = save_entry.get().strip()
            config["noita_exe_path"] = exe_entry.get().strip()
            config["saves_dir"] = saves_entry.get().strip()
            # дополнительные параметры
            config["save_name_format"] = format_entry.get().strip() or "%Y-%m-%d_%H-%M-%S"
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

            # обновим подписи и список слотов
            self.label_save_path.config(
                text=f"save00: {config['noita_save_path']}"
            )
            self.label_exe_path.config(
                text=f"Noita.exe: {config['noita_exe_path']}"
            )
            self.refresh_slots_list()

            # применить тему сразу
            try:
                self.apply_theme(config.get("theme", "light"))
            except Exception:
                pass

            messagebox.showinfo("Настройки", "Настройки сохранены.")
            win.destroy()

        # Нижняя фиксированная панель с кнопками: Сохранить, Сброс пути, Сброс настроек, Закрыть
        bottom_btns = ttk.Frame(win)
        bottom_btns.pack(fill="x", side="bottom", padx=8, pady=8)

        def _reset_paths():
            # дефолтные пути
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
            self.apply_theme("light")

        ttk.Button(bottom_btns, text="Установить пути по умолчанию", command=_reset_paths).pack(side="left", padx=6)
        ttk.Button(bottom_btns, text="Установить остальные по умолчанию", command=_reset_other).pack(side="left", padx=6)
        ttk.Button(bottom_btns, text="Сохранить", command=save_settings).pack(side="right", padx=6)
        ttk.Button(bottom_btns, text="Закрыть", command=win.destroy).pack(side="right", padx=6)

        self.apply_theme(config.get("theme", "light"), root_widget=win)
        win.grab_set()  # модальное окно

    def apply_theme(self, theme_name: str, root_widget=None):
        """Apply a more complete light/dark theme to ttk and tk widgets."""
        target = root_widget or self
        style = ttk.Style(target)
        theme = theme_name or config.get("theme", "light")

        if theme == "dark":
            bg = "#1f1f1f"
            fg = "#e6e6e6"
            btn_bg = "#2d2d2d"
            entry_bg = "#2d2d2d"
            accent = "#3a3a3a"
            disabled_fg = "#7a7a7a"
        else:
            bg = "#ffffff"
            fg = "#000000"
            btn_bg = "#f0f0f0"
            entry_bg = "#ffffff"
            accent = "#e2e2e2"
            disabled_fg = "#888888"

        try:
            # Use a theme that respects custom colors
            try:
                style.theme_use("clam")
            except Exception:
                pass

            style.configure("TFrame", background=bg)
            style.configure("TLabel", background=bg, foreground=fg)
            style.configure("TButton", background=btn_bg, foreground=fg)
            style.configure("TCheckbutton", background=bg, foreground=fg)
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
