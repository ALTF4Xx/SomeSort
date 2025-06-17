#!/usr/bin/env python3

import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import logging

TOOL_NAME = "SomeSort"

def setup_installation():
    root_temp = tk.Tk()
    root_temp.withdraw()
    install_path = filedialog.askdirectory(title=f"{TOOL_NAME} - Select Installation Directory")
    if not install_path:
        messagebox.showerror("Setup Cancelled", "Installation location not selected. Exiting.")
        exit()

    # Change here: Big folder named "SomeSort Main"
    install_path = os.path.join(install_path, f"{TOOL_NAME} Main")

    logs_path = os.path.join(install_path, "LOGS")
    readme_path = os.path.join(install_path, "README")
    sorted_files_path = os.path.join(install_path, "SortedFiles")

    os.makedirs(logs_path, exist_ok=True)
    os.makedirs(readme_path, exist_ok=True)
    os.makedirs(sorted_files_path, exist_ok=True)

    readme_file = os.path.join(readme_path, "README.txt")
    if not os.path.isfile(readme_file):
        with open(readme_file, "w") as f:
            f.write(
                "Thank you for using my lightweight tool that sorts files for you! Please consider keeping up with my future projects : )\n\n"
                "Maintainer : Leonardo Romano (cubemasterplayer)\n"
                "Version 1.0\n"
            )

    messagebox.showinfo(
        f"{TOOL_NAME} Installed",
        f"{TOOL_NAME} has been installed at:\n{install_path}\n\n"
        f"Logs will be saved to:\n{logs_path}\n"
        f"Sorted files will be placed in:\n{sorted_files_path}"
    )

    root_temp.destroy()
    return install_path, logs_path, sorted_files_path

INSTALL_DIR, LOG_DIR, SORTED_DIR = setup_installation()
LOG_FILE = os.path.join(LOG_DIR, "file_sorter.log")

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(message)s')

CATEGORIES = {
    "Images": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".svg", ".webp", ".heic"
    ],
    "Documents": [
        ".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md", ".tex"
    ],
    "Videos": [
        ".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".mpeg", ".mpg", ".webm", ".3gp"
    ],
    "Music": [
        ".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".alac"
    ],
    "Archives": [
        ".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz", ".lzma", ".iso"
    ],
    "Scripts": [
        ".py", ".sh", ".bat", ".js", ".pl", ".rb", ".php", ".ps1", ".lua", ".groovy"
    ],
    "Fonts": [
        ".ttf", ".otf", ".woff", ".woff2", ".eot"
    ],
    "Spreadsheets": [
        ".xls", ".xlsx", ".ods", ".csv"
    ],
    "Presentations": [
        ".ppt", ".pptx", ".odp"
    ],
    "Executables": [
        ".exe", ".msi", ".apk", ".bin", ".appimage"
    ],
    "Others": []
}

def get_category(filename):
    ext = os.path.splitext(filename)[1].lower()
    for category, extensions in CATEGORIES.items():
        if ext in extensions:
            return category
    return "Others"

def sort_file(file_path, destination_root):
    if not os.path.isfile(file_path):
        return None
    category = get_category(file_path)
    target_dir = os.path.join(destination_root, category)
    os.makedirs(target_dir, exist_ok=True)
    try:
        dest_path = os.path.join(target_dir, os.path.basename(file_path))
        shutil.move(file_path, dest_path)
        logging.info(f"Moved: {file_path} → {dest_path}")
        return os.path.basename(file_path)
    except Exception as e:
        logging.error(f"Failed to move {file_path}: {e}")
        messagebox.showerror("Error", f"Failed to move file:\n{e}")
        return None

def on_drop(event):
    files = root.tk.splitlist(event.data)
    last_file = None
    for file_path in files:
        filename = sort_file(file_path, destination_folder.get())
        if filename:
            last_file = filename
    if last_file:
        status_label.config(text=f"Last sorted file: {last_file}")
    messagebox.showinfo("Done", "Files sorted successfully.")

class WatchHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1)
            filename = sort_file(event.src_path, destination_folder.get())
            if filename:
                status_label.config(text=f"Last sorted file: {filename}")

def start_watching(path):
    observer = Observer()
    handler = WatchHandler()
    observer.schedule(handler, path=path, recursive=False)
    observer.start()
    logging.info(f"Started watching folder: {path}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def choose_watch_folder():
    path = filedialog.askdirectory(title="Select folder to watch")
    if path:
        watch_label.config(text=f"Watching: {path}")
        thread = threading.Thread(target=start_watching, args=(path,), daemon=True)
        thread.start()

def choose_destination():
    path = filedialog.askdirectory(title="Select destination folder")
    if path:
        destination_folder.set(path)
        dest_label.config(text=f"Destination: {path}")

root = TkinterDnD.Tk()
root.title(TOOL_NAME)
root.geometry("1000x600")
root.resizable(False, False)
root.configure(bg="#2e2e2e")

frame = tk.Frame(root, bg="#2e2e2e")
frame.place(relwidth=1, relheight=1)

label_font = ("Arial", 18, "bold")
small_font = ("Arial", 11)

tk.Label(frame, text="Drag and drop files here to sort them :)", fg="white", bg="#2e2e2e", font=label_font).pack(pady=25)

drop_zone = tk.Label(
    frame,
    text="🗂️ Drop Files Here",
    relief="ridge",
    width=60,
    height=8,
    bg="#444444",
    fg="white",
    font=("Arial", 24, "bold"),
    bd=2,
    highlightthickness=0
)
drop_zone.pack(pady=15)
drop_zone.drop_target_register(DND_FILES)
drop_zone.dnd_bind('<<Drop>>', on_drop)

status_label = tk.Label(frame, text="Last sorted file: None", fg="#bbbbbb", bg="#2e2e2e", font=("Arial", 10, "italic"))
status_label.pack(pady=(5, 20))

btn_frame = tk.Frame(frame, bg="#2e2e2e")
btn_frame.pack(pady=20)

button_style = {
    "bg": "#555555",
    "fg": "white",
    "activebackground": "#777777",
    "activeforeground": "white",
    "font": ("Arial", 14),
    "bd": 0,
    "relief": "flat",
    "width": 20,
    "cursor": "hand2",
}

tk.Button(btn_frame, text="Choose Destination", command=choose_destination, **button_style).grid(row=0, column=0, padx=20)
tk.Button(btn_frame, text="Watch a Folder", command=choose_watch_folder, **button_style).grid(row=0, column=1, padx=20)

destination_folder = tk.StringVar(value=SORTED_DIR)

dest_label = tk.Label(frame, text=f"Destination: {destination_folder.get()}", fg="white", bg="#2e2e2e", font=small_font)
dest_label.pack(pady=10)

watch_label = tk.Label(frame, text="Watching: None", fg="white", bg="#2e2e2e", font=small_font)
watch_label.pack(pady=10)

tk.Label(frame, text=f"(Logs saved to {LOG_FILE})", fg="white", bg="#2e2e2e", font=("Arial", 9)).pack(side="bottom", pady=15)

root.mainloop()
