"""程序入口：启动小工具箱 GUI。"""

import tkinter as tk

from app import GadgetApp


def main() -> None:
    """创建并启动主窗口。"""
    root = tk.Tk()
    GadgetApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
