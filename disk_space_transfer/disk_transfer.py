# -*- coding: utf-8 -*-
"""
Windows 磁盘空间分配工具
功能：将指定磁盘（如 D 盘）的未使用空间划拨给另一个磁盘（如 C 盘）
原理：通过 Windows diskpart 工具收缩源磁盘并扩展目标磁盘

⚠️  注意事项：
    1. 必须以【管理员身份】运行
    2. 分区操作不可逆，请提前备份重要数据
    3. 仅支持 NTFS 分区
    4. 扩展目标分区需要其右侧紧邻未分配空间
"""

import ctypes
import os
import subprocess
import sys
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk


# ---------------------------------------------------------------------------
# 权限检查
# ---------------------------------------------------------------------------

def is_admin() -> bool:
    """判断当前进程是否拥有管理员权限。"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def relaunch_as_admin():
    """以管理员身份重新启动本脚本。"""
    script = os.path.abspath(sys.argv[0])
    params = " ".join(f'"{a}"' for a in sys.argv[1:])
    ret = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{script}" {params}', None, 1
    )
    if ret <= 32:
        messagebox.showerror("权限错误", "无法获取管理员权限，请手动以管理员身份运行。")
    sys.exit(0)


# ---------------------------------------------------------------------------
# diskpart 操作封装
# ---------------------------------------------------------------------------

def run_diskpart(script_lines: list) -> tuple:
    """
    将 diskpart 命令写入临时脚本文件并执行。
    返回 (成功与否, 输出文本)。
    """
    script_content = "\r\n".join(script_lines) + "\r\n"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="gbk"
    ) as f:
        f.write(script_content)
        tmp_path = f.name

    try:
        result = subprocess.run(
            ["diskpart", "/s", tmp_path],
            capture_output=True,
            text=True,
            encoding="gbk",
            errors="replace",
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output
    finally:
        os.unlink(tmp_path)


def get_volume_info() -> str:
    """获取所有卷（分区）信息。"""
    _, output = run_diskpart(["list volume"])
    return output


def shrink_volume(drive_letter: str, shrink_mb: int) -> tuple:
    """
    收缩指定盘符对应的卷。
    drive_letter: 不含冒号，如 'D'
    shrink_mb: 要收缩的大小（MB）
    """
    script = [
        f"select volume {drive_letter}",
        f"shrink desired={shrink_mb}",
    ]
    return run_diskpart(script)


def extend_volume(drive_letter: str, extend_mb: int) -> tuple:
    """
    扩展指定盘符对应的卷。
    drive_letter: 不含冒号，如 'C'
    extend_mb: 要扩展的大小（MB），0 表示使用全部可用未分配空间
    """
    size_param = f"size={extend_mb}" if extend_mb > 0 else ""
    script = [
        f"select volume {drive_letter}",
        f"extend {size_param}".strip(),
    ]
    return run_diskpart(script)


# ---------------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------------

class DiskTransferApp(tk.Tk):
    """磁盘空间分配工具主界面。"""

    DRIVE_LETTERS = [chr(c) for c in range(ord('A'), ord('Z') + 1)]

    def __init__(self):
        super().__init__()
        self.title("磁盘空间分配工具 - Wonderful Little Gadgets")
        self.resizable(False, False)
        self._build_ui()
        self._center_window()

    # ------------------------------------------------------------------
    # UI 构建
    # ------------------------------------------------------------------

    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}

        # ---- 标题 ----
        title_frame = tk.Frame(self, bg="#2c3e50")
        title_frame.pack(fill=tk.X)
        tk.Label(
            title_frame,
            text="  Windows 磁盘空间分配工具",
            font=("微软雅黑", 14, "bold"),
            fg="white",
            bg="#2c3e50",
            pady=10,
        ).pack()

        # ---- 警告条 ----
        warn_frame = tk.Frame(self, bg="#f39c12")
        warn_frame.pack(fill=tk.X)
        tk.Label(
            warn_frame,
            text="⚠  操作不可逆！请提前备份数据，并确保以管理员身份运行",
            font=("微软雅黑", 9),
            fg="white",
            bg="#f39c12",
            pady=4,
        ).pack()

        main = tk.Frame(self, padx=20, pady=10)
        main.pack()

        # ---- 源磁盘（被收缩） ----
        src_frame = ttk.LabelFrame(main, text="源磁盘（将被压缩 / 释放空间）", padding=10)
        src_frame.grid(row=0, column=0, sticky="ew", **pad)

        tk.Label(src_frame, text="选择盘符：").grid(row=0, column=0, sticky="w")
        self.src_drive = ttk.Combobox(
            src_frame, values=self.DRIVE_LETTERS, width=5, state="readonly"
        )
        self.src_drive.set("D")
        self.src_drive.grid(row=0, column=1, sticky="w", padx=(4, 0))

        tk.Label(src_frame, text="压缩大小（GB）：").grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.shrink_gb = ttk.Spinbox(src_frame, from_=1, to=9999, increment=1, width=8)
        self.shrink_gb.set("10")
        self.shrink_gb.grid(row=1, column=1, sticky="w", padx=(4, 0), pady=(6, 0))

        # ---- 目标磁盘（被扩展） ----
        dst_frame = ttk.LabelFrame(main, text="目标磁盘（将获得空间）", padding=10)
        dst_frame.grid(row=1, column=0, sticky="ew", **pad)

        tk.Label(dst_frame, text="选择盘符：").grid(row=0, column=0, sticky="w")
        self.dst_drive = ttk.Combobox(
            dst_frame, values=self.DRIVE_LETTERS, width=5, state="readonly"
        )
        self.dst_drive.set("C")
        self.dst_drive.grid(row=0, column=1, sticky="w", padx=(4, 0))

        tk.Label(dst_frame, text="扩展大小（GB，0=全部）：").grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )
        self.extend_gb = ttk.Spinbox(dst_frame, from_=0, to=9999, increment=1, width=8)
        self.extend_gb.set("0")
        self.extend_gb.grid(row=1, column=1, sticky="w", padx=(4, 0), pady=(6, 0))

        # ---- 操作按钮 ----
        btn_frame = tk.Frame(main)
        btn_frame.grid(row=2, column=0, pady=(4, 0))

        ttk.Button(
            btn_frame, text="查看磁盘信息", command=self._show_disk_info
        ).grid(row=0, column=0, padx=6)

        ttk.Button(
            btn_frame, text="仅压缩源磁盘", command=self._do_shrink_only
        ).grid(row=0, column=1, padx=6)

        ttk.Button(
            btn_frame, text="仅扩展目标磁盘", command=self._do_extend_only
        ).grid(row=0, column=2, padx=6)

        ttk.Button(
            btn_frame,
            text="一键：压缩 + 扩展",
            command=self._do_transfer,
        ).grid(row=1, column=0, columnspan=3, pady=(8, 0), ipadx=10, ipady=4)

        # ---- 日志输出 ----
        log_frame = ttk.LabelFrame(main, text="操作日志", padding=6)
        log_frame.grid(row=3, column=0, sticky="ew", **pad)

        self.log_text = tk.Text(
            log_frame, height=12, width=64, state=tk.DISABLED,
            font=("Consolas", 9), bg="#1e1e1e", fg="#d4d4d4",
            relief=tk.FLAT
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _center_window(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    # ------------------------------------------------------------------
    # 日志辅助
    # ------------------------------------------------------------------

    def _log(self, msg: str):
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.update()

    def _log_separator(self):
        self._log("-" * 60)

    # ------------------------------------------------------------------
    # 输入校验
    # ------------------------------------------------------------------

    def _validate_inputs(self, need_src=True, need_dst=True):
        src = self.src_drive.get().strip().upper()
        dst = self.dst_drive.get().strip().upper()
        try:
            shrink_mb = int(float(self.shrink_gb.get()) * 1024) if need_src else 0
        except ValueError:
            messagebox.showerror("输入错误", "压缩大小必须是数字！")
            return None
        try:
            extend_gb_val = float(self.extend_gb.get())
            extend_mb = int(extend_gb_val * 1024) if need_dst else 0
        except ValueError:
            messagebox.showerror("输入错误", "扩展大小必须是数字！")
            return None

        if need_src and shrink_mb <= 0:
            messagebox.showerror("输入错误", "压缩大小必须大于 0 GB！")
            return None
        if need_src and need_dst and src == dst:
            messagebox.showerror("输入错误", "源磁盘和目标磁盘不能相同！")
            return None
        return src, dst, shrink_mb, extend_mb

    # ------------------------------------------------------------------
    # 按钮回调
    # ------------------------------------------------------------------

    def _show_disk_info(self):
        self._log_separator()
        self._log("[信息] 正在获取磁盘信息...")
        info = get_volume_info()
        self._log(info)

    def _do_shrink_only(self):
        result = self._validate_inputs(need_src=True, need_dst=False)
        if result is None:
            return
        src, _, shrink_mb, _ = result
        if not messagebox.askyesno(
            "确认操作",
            f"即将压缩 {src} 盘 {shrink_mb / 1024:.1f} GB\n\n此操作不可撤销，是否继续？"
        ):
            return
        self._log_separator()
        self._log(f"[操作] 压缩 {src} 盘，大小 {shrink_mb} MB...")
        ok, out = shrink_volume(src, shrink_mb)
        self._log(out)
        if ok:
            self._log(f"[成功] {src} 盘压缩完成！")
            messagebox.showinfo("完成", f"{src} 盘压缩完成！\n可在磁盘管理中看到未分配空间。")
        else:
            self._log("[失败] 压缩操作未成功，请查看日志。")
            messagebox.showerror("失败", "压缩操作失败，请查看日志。")

    def _do_extend_only(self):
        result = self._validate_inputs(need_src=False, need_dst=True)
        if result is None:
            return
        _, dst, _, extend_mb = result
        size_desc = f"{extend_mb / 1024:.1f} GB" if extend_mb > 0 else "全部未分配空间"
        if not messagebox.askyesno(
            "确认操作",
            f"即将扩展 {dst} 盘 {size_desc}\n\n此操作不可撤销，是否继续？"
        ):
            return
        self._log_separator()
        self._log(f"[操作] 扩展 {dst} 盘，大小 {size_desc}...")
        ok, out = extend_volume(dst, extend_mb)
        self._log(out)
        if ok:
            self._log(f"[成功] {dst} 盘扩展完成！")
            messagebox.showinfo("完成", f"{dst} 盘扩展完成！")
        else:
            self._log("[失败] 扩展操作未成功，请查看日志。")
            messagebox.showerror("失败", "扩展操作失败，请查看日志。")

    def _do_transfer(self):
        result = self._validate_inputs(need_src=True, need_dst=True)
        if result is None:
            return
        src, dst, shrink_mb, extend_mb = result
        size_desc = f"{extend_mb / 1024:.1f} GB" if extend_mb > 0 else "全部释放的空间"
        if not messagebox.askyesno(
            "确认操作",
            f"操作摘要：\n"
            f"  · 压缩 {src} 盘  {shrink_mb / 1024:.1f} GB\n"
            f"  · 扩展 {dst} 盘  {size_desc}\n\n"
            "此操作不可撤销，请确保已备份数据！\n\n是否继续？"
        ):
            return

        self._log_separator()
        # Step 1: 收缩
        self._log(f"[步骤 1/2] 压缩 {src} 盘 {shrink_mb} MB...")
        ok, out = shrink_volume(src, shrink_mb)
        self._log(out)
        if not ok:
            self._log("[失败] 压缩步骤失败，已中止后续操作。")
            messagebox.showerror("失败", "压缩操作失败，已停止。请查看日志。")
            return
        self._log(f"[成功] {src} 盘压缩完成。")

        # Step 2: 扩展
        self._log(f"[步骤 2/2] 扩展 {dst} 盘 {size_desc}...")
        ok, out = extend_volume(dst, extend_mb)
        self._log(out)
        if ok:
            self._log(f"[成功] {dst} 盘扩展完成！全部操作已完成。")
            messagebox.showinfo(
                "完成",
                f"操作成功！\n\n{src} 盘已压缩 {shrink_mb / 1024:.1f} GB\n{dst} 盘已扩展 {size_desc}"
            )
        else:
            self._log("[失败] 扩展步骤失败，请查看日志。")
            messagebox.showerror(
                "部分失败",
                f"{src} 盘已压缩成功，但 {dst} 盘扩展失败。\n"
                "请打开"磁盘管理"手动扩展，或检查分区布局是否符合要求。"
            )


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not is_admin():
        relaunch_as_admin()
    else:
        app = DiskTransferApp()
        app.mainloop()
