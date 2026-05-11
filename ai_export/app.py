"""主窗口框架：负责 Notebook 与插件自动加载。"""

from __future__ import annotations

import importlib
import inspect
from pathlib import Path
import tkinter as tk
from tkinter import ttk

from plugins.base_plugin import BasePlugin


class GadgetApp:
    """小工具箱主应用。"""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🛠 小工具箱")
        self.root.geometry("680x560")
        self.root.minsize(680, 560)

        self._set_style()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._load_plugins()

    def _set_style(self) -> None:
        """设置 ttk 主题为现代风格。"""
        style = ttk.Style(self.root)
        for theme in ("vista", "clam"):
            if theme in style.theme_names():
                style.theme_use(theme)
                break

    def _load_plugins(self) -> None:
        """扫描 plugins 目录并自动加载所有插件。"""
        plugins_dir = Path(__file__).resolve().parent / "plugins"
        plugin_files = sorted(
            path for path in plugins_dir.glob("*.py") if path.stem not in {"__init__", "base_plugin"}
        )

        loaded = 0
        for plugin_file in plugin_files:
            module_name = f"plugins.{plugin_file.stem}"
            try:
                module = importlib.import_module(module_name)
            except Exception as exc:  # noqa: BLE001
                print(f"插件导入失败 {module_name}: {exc}")
                continue

            plugin_classes = [
                cls
                for _, cls in inspect.getmembers(module, inspect.isclass)
                if issubclass(cls, BasePlugin) and cls is not BasePlugin and cls.__module__ == module.__name__
            ]

            for plugin_cls in plugin_classes:
                try:
                    plugin = plugin_cls()
                    tab = ttk.Frame(self.notebook)
                    plugin.build_ui(tab)
                    self.notebook.add(tab, text=plugin.name)
                    loaded += 1
                except Exception as exc:  # noqa: BLE001
                    print(f"插件实例化失败 {plugin_cls.__name__}: {exc}")

        if loaded == 0:
            empty = ttk.Frame(self.notebook)
            ttk.Label(empty, text="未检测到可用插件", anchor="center").pack(fill="both", expand=True, padx=20, pady=20)
            self.notebook.add(empty, text="提示")
