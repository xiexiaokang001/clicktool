import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config import Config
from src.ocr import ScreenOCR
from src.clicker import Clicker


class ClickToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ClickTool - 屏幕文字识别自动点击工具")
        self.root.geometry("620x520")
        self.root.resizable(True, True)

        self.is_running = False
        self.stop_event = threading.Event()
        self.was_minimized = False

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        target_frame = ttk.LabelFrame(main_frame, text=" 目标设置 ", padding="10")
        target_frame.pack(fill=tk.X, pady=5)

        ttk.Label(target_frame, text="目标文字（多个用逗号分隔）:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_entry = ttk.Entry(target_frame, width=55)
        self.target_entry.grid(row=0, column=1, columnspan=2, pady=5, padx=5)

        ttk.Label(target_frame, text="每个目标点击次数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.click_number = ttk.Spinbox(target_frame, from_=1, to=999, width=10)
        self.click_number.set(1)
        self.click_number.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        ttk.Label(target_frame, text="点击间隔（秒）:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)
        self.interval = ttk.Spinbox(target_frame, from_=0.5, to=3600, width=10)
        self.interval.set(2.0)
        self.interval.grid(row=1, column=2, sticky=tk.W, pady=5, padx=5)

        config_frame = ttk.LabelFrame(main_frame, text=" 配置 ", padding="10")
        config_frame.pack(fill=tk.X, pady=5)

        ttk.Label(config_frame, text="配置文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.config_path = ttk.Entry(config_frame, width=55)
        self.config_path.insert(0, "config.yaml")
        self.config_path.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(config_frame, text="置信度阈值（0.1-1.0）:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.confidence = ttk.Spinbox(config_frame, from_=0.1, to=1.0, width=10)
        self.confidence.set(0.8)
        self.confidence.grid(row=1, column=1, sticky=tk.W, pady=5, padx=5)

        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(button_frame, text="开始执行", command=self.start_task, width=15)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(button_frame, text="停止", command=self.stop_task, state=tk.DISABLED, width=15)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(button_frame, text="清空日志", command=self.clear_log, width=15)
        self.clear_btn.pack(side=tk.RIGHT, padx=5)

        self.minimize_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(button_frame, text="运行时最小化窗口", variable=self.minimize_var).pack(side=tk.LEFT, padx=20)

        log_frame = ttk.LabelFrame(main_frame, text=" 运行日志 ", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.status_var = tk.StringVar(value="就绪 - 输入目标文字后点击开始执行")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def log(self, message):
        self.root.after(0, self._log, message)

    def _log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def update_status(self, status):
        self.root.after(0, self.status_var.set, status)

    def get_config(self):
        config = Config(self.config_path.get())
        config.config['ocr'] = config.config.get('ocr', {})
        config.config['ocr']['confidence'] = float(self.confidence.get())
        return config

    def minimize_window(self):
        self.was_minimized = self.root.state() == 'normal'
        self.root.iconify()

    def restore_window(self):
        self.root.deiconify()
        self.root.lift()

    def run_click_task(self, target_text, config):
        ocr = ScreenOCR(config)
        clicker = Clicker(config)

        self.log(f"正在查找文字: {target_text}")
        position = ocr.get_text_position(target_text)

        if position:
            x, y = position
            self.log(f"找到目标位置: ({x}, {y})")
            clicker.click(x, y)
            self.log(f"点击完成")
            return True
        else:
            self.log(f"未找到文字: {target_text}")
            return False

    def start_task(self):
        if self.is_running:
            return

        targets_input = self.target_entry.get().strip()
        if not targets_input:
            messagebox.showwarning("警告", "请输入目标文字")
            return

        targets = [t.strip() for t in targets_input.split(',')]
        click_num = int(self.click_number.get())
        interval = float(self.interval.get())

        self.is_running = True
        self.stop_event.clear()
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.target_entry.config(state=tk.DISABLED)

        if self.minimize_var.get():
            self.minimize_window()

        def task_thread():
            try:
                config = self.get_config()

                for i, target in enumerate(targets):
                    if not self.is_running:
                        break

                    self.update_status(f"正在处理目标 {i+1}/{len(targets)}: {target}")
                    self.log(f"=== 目标 {i+1}/{len(targets)}: {target} ===")

                    for j in range(click_num):
                        if not self.is_running:
                            break

                        if j > 0 or i > 0:
                            self.log(f"等待 {interval} 秒...")
                            for k in range(int(interval * 10)):
                                if not self.is_running:
                                    break
                                time.sleep(0.1)

                        self.run_click_task(target, config)

                    self.log(f"=== 完成目标 {i+1}/{len(targets)}: {target} ===")

                if self.is_running:
                    self.log("所有任务完成！")
                    self.update_status("完成 - 点击开始执行可再次运行")
                else:
                    self.log("任务已停止")
                    self.update_status("已停止 - 点击开始执行可再次运行")

            except Exception as e:
                self.log(f"错误: {str(e)}")
                self.update_status("发生错误")
            finally:
                self.is_running = False
                self.root.after(0, self.finish_task)

        threading.Thread(target=task_thread, daemon=True).start()

    def stop_task(self):
        self.is_running = False
        self.stop_event.set()
        self.log("正在停止任务...")
        self.update_status("正在停止...")

    def finish_task(self):
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.target_entry.config(state=tk.NORMAL)
        self.restore_window()


def main():
    root = tk.Tk()
    app = ClickToolGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
