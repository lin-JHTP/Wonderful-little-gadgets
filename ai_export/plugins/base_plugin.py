from abc import ABC, abstractmethod
from tkinter import ttk


class BasePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """插件显示名称（用于 Tab 标签）"""

    @abstractmethod
    def build_ui(self, parent: ttk.Frame) -> None:
        """在 parent 框架中构建该插件的 UI"""
