"""AI 内容导出插件。"""

from __future__ import annotations

from pathlib import Path
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from core.detector import detect_format
from core.file_writer import write_file
from plugins.base_plugin import BasePlugin


class AIExportPlugin(BasePlugin):
    """将粘贴内容自动识别并导出为文件。"""

    def __init__(self) -> None:
        self._title_placeholder = "请输入文件标题，留空则自动生成"
        self._output_dir = self._default_desktop()
        self._latest_file: Path | None = None

    @property
    def name(self) -> str:
        return "AI内容导出"

    def build_ui(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        top = ttk.Frame(parent)
        top.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 6))
        top.columnconfigure(1, weight=1)

        ttk.Label(top, text="文件标题：").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.title_entry = tk.Entry(top, fg="gray")
        self.title_entry.grid(row=0, column=1, sticky="ew")
        self.title_entry.insert(0, self._title_placeholder)
        self.title_entry.bind("<FocusIn>", self._on_title_focus_in)
        self.title_entry.bind("<FocusOut>", self._on_title_focus_out)

        editor_frame = ttk.Frame(parent)
        editor_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=6)
        editor_frame.columnconfigure(0, weight=1)
        editor_frame.rowconfigure(0, weight=1)

        self.content_text = tk.Text(editor_frame, wrap="word")
        self.content_text.grid(row=0, column=0, sticky="nsew")

        yscroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self.content_text.yview)
        yscroll.grid(row=0, column=1, sticky="ns")
        self.content_text.configure(yscrollcommand=yscroll.set)

        folder_frame = ttk.Frame(parent)
        folder_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=6)
        folder_frame.columnconfigure(1, weight=1)

        ttk.Label(folder_frame, text="输出文件夹：").grid(row=0, column=0, sticky="w", padx=(0, 6))
        self.output_var = tk.StringVar(value=str(self._output_dir))
        ttk.Label(folder_frame, textvariable=self.output_var).grid(row=0, column=1, sticky="w")
        ttk.Button(folder_frame, text="浏览", command=self._choose_folder).grid(row=0, column=2, padx=(8, 0))

        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, sticky="e", padx=10, pady=(2, 6))
        ttk.Button(button_frame, text="清空", command=self._clear_all).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_frame, text="生成文件", command=self._generate_file).grid(row=0, column=1)

        status_frame = ttk.Frame(parent)
        status_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="状态：等待输入内容")
        ttk.Label(status_frame, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        self.open_button = ttk.Button(status_frame, text="打开文件夹", command=self._open_folder, state="disabled")
        self.open_button.grid(row=0, column=1, padx=(8, 0))

    def _on_title_focus_in(self, _: tk.Event) -> None:
        if self.title_entry.get() == self._title_placeholder:
            self.title_entry.delete(0, tk.END)
            self.title_entry.configure(fg="black")

    def _on_title_focus_out(self, _: tk.Event) -> None:
        if not self.title_entry.get().strip():
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self._title_placeholder)
            self.title_entry.configure(fg="gray")

    def _get_title(self) -> str:
        value = self.title_entry.get().strip()
        if value == self._title_placeholder:
            return ""
        return value

    def _default_desktop(self) -> Path:
        return Path.home() / "Desktop"

    def _choose_folder(self) -> None:
        folder = filedialog.askdirectory(initialdir=str(self._output_dir), title="选择输出文件夹")
        if folder:
            self._output_dir = Path(folder)
            self.output_var.set(folder)

    def _clear_all(self) -> None:
        self.content_text.delete("1.0", tk.END)
        self.status_var.set("状态：已清空")
        self._latest_file = None
        self.open_button.configure(state="disabled")

    def _generate_file(self) -> None:
        content = self.content_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("提示", "请先粘贴需要导出的内容")
            return

        try:
            detection = detect_format(content)
            title = self._get_title()
            file_path = write_file(content, title, self._output_dir, detection)
            self._latest_file = file_path
            self.status_var.set(f"检测格式：{detection.format_label} | 已生成：{file_path}")
            self.open_button.configure(state="normal")
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("错误", f"生成文件失败：{exc}")

    def _open_folder(self) -> None:
        folder = self._output_dir
        if not folder.exists():
            messagebox.showwarning("提示", "输出文件夹不存在")
            return

        if os.name == "nt":
            os.startfile(folder)  # type: ignore[attr-defined]
            return

        webbrowser.open(folder.resolve().as_uri())
