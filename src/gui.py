"""
图形界面模块
使用 Tkinter 构建简单易用的界面
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk
import cv2
import numpy as np
from typing import Optional

from .matcher import IconMatcher


class JX3DetectorGUI:
    def __init__(self, assets_dir: Path):
        self.assets_dir = Path(assets_dir)
        self.matcher = IconMatcher(assets_dir)
        
        self.root = tk.Tk()
        self.root.title("剑网三门派识别工具")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        self._setup_ui()
        self.current_screenshot: Optional[np.ndarray] = None
        self.result_labels: list = []

    def _setup_ui(self):
        """构建界面"""
        # 标题
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(fill="x")
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame,
            text="🎮 剑网三门派识别工具",
            font=("微软雅黑", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        ).pack(pady=15)
        
        # 主内容区
        content = tk.Frame(self.root, bg="#ecf0f1")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 左侧：图片显示区
        left_frame = tk.Frame(content, bg="white", width=250, height=350)
        left_frame.pack(side="left", fill="both", padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="截图预览", font=("微软雅黑", 11), bg="white").pack(pady=5)
        
        self.img_label = tk.Label(left_frame, text="未加载图片\n\n请按 F9 截图\n或点击下方按钮选择",
                                  font=("微软雅黑", 10), bg="#f0f0f0", fg="#888",
                                  width=30, height=12)
        self.img_label.pack(padx=10, pady=5)
        
        # 按钮区
        btn_frame = tk.Frame(left_frame, bg="white")
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="📂 选择图片", command=self.select_image,
                 font=("微软雅黑", 10), width=12).grid(row=0, column=0, padx=5, pady=3)
        
        tk.Button(btn_frame, text="🔍 开始识别", command=self.do_recognize,
                 font=("微软雅黑", 10), width=12, bg="#3498db", fg="white").grid(row=1, column=0, padx=5, pady=3)
        
        tk.Button(btn_frame, text="🗑️ 清除", command=self.clear,
                 font=("微软雅黑", 10), width=12).grid(row=2, column=0, padx=5, pady=3)
        
        # 右侧：识别结果区
        right_frame = tk.Frame(content, bg="white", width=300, height=350)
        right_frame.pack(side="right", fill="both")
        right_frame.pack_propagate(False)
        
        tk.Label(right_frame, text="识别结果", font=("微软雅黑", 11), bg="white").pack(pady=5)
        
        # 结果列表容器
        result_container = tk.Frame(right_frame, bg="white")
        result_container.pack(fill="both", expand=True, padx=10)
        
        self.result_canvas = tk.Canvas(result_container, bg="white", highlightthickness=0)
        scrollbar = ttk.Scrollbar(result_container, orient="vertical", command=self.result_canvas.yview)
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.result_inner = tk.Frame(self.result_canvas, bg="white")
        self.result_canvas.create_window((0, 0), window=self.result_inner, anchor="nw")
        
        self.result_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.result_inner.bind("<Configure>", 
            lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all")))
        
        # 底部状态栏
        self.status_label = tk.Label(
            self.root, text="状态: 就绪  |  按 F9 监听剪贴板截图",
            font=("微软雅黑", 9), bd=1, anchor="w"
        )
        self.status_label.pack(fill="x", padx=20, pady=(0, 5))
        
        self.info_label = tk.Label(
            self.root, text=f"已加载 {self.matcher.template_cache.__len__()} 个门派图标",
            font=("微软雅黑", 9), bd=1, anchor="w"
        )
        self.info_label.pack(fill="x", padx=20, pady=(0, 10))

    def set_screenshot(self, img_array: np.ndarray):
        """设置截图并显示"""
        self.current_screenshot = img_array
        
        # 转换并缩放显示
        display = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        h, w = display.shape[:2]
        scale = min(220/w, 280/h)
        display = cv2.resize(display, (int(w*scale), int(h*scale)))
        
        img_pil = Image.fromarray(display)
        img_tk = ImageTk.PhotoImage(img_pil)
        
        self.img_label.configure(image=img_tk, text="", width=30, height=12)
        self.img_label.image = img_tk  # 保持引用
        self.status_label.configure(text="状态: 图片已加载，请点击「开始识别」")

    def select_image(self):
        """选择图片文件"""
        path = filedialog.askopenfilename(
            title="选择门派图标截图",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp"), ("所有文件", "*.*")]
        )
        if path:
            img = cv2.imread(path)
            if img is not None:
                self.set_screenshot(img)
            else:
                messagebox.showerror("错误", "无法读取图片文件")

    def do_recognize(self):
        """执行识别"""
        if self.current_screenshot is None:
            messagebox.showwarning("提示", "请先加载图片")
            return
        
        self.status_label.configure(text="状态: 识别中...")
        self.root.update()
        
        try:
            results = self.matcher.match(self.current_screenshot, threshold=0.5)
            self.display_results(results)
            
            if results:
                self.status_label.configure(text=f"状态: 识别完成，匹配到 {len(results)} 个可能结果")
            else:
                self.status_label.configure(text="状态: 未匹配到任何门派")
        except Exception as e:
            messagebox.showerror("识别错误", str(e))
            self.status_label.configure(text="状态: 识别失败")

    def display_results(self, results: list[tuple[str, float]]):
        """显示识别结果"""
        # 清除旧结果
        for widget in self.result_inner.winfo_children():
            widget.destroy()
        
        if not results:
            tk.Label(self.result_inner, text="❌ 无法识别\n\n请检查截图是否包含门派图标",
                    font=("微软雅黑", 11), bg="white", fg="#e74c3c").pack(pady=20)
            return
        
        # 显示前5个结果
        for i, (name, score) in enumerate(results[:5]):
            bg = "#e8f5e9" if i == 0 else "white"
            fg = "#27ae60" if i == 0 else "#2c3e50"
            
            frame = tk.Frame(self.result_inner, bg=bg, relief="flat", bd=1)
            frame.pack(fill="x", pady=2)
            
            rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            
            tk.Label(frame, text=f"{rank} {name}", font=("微软雅黑", 11, "bold"),
                    bg=bg, fg=fg).pack(side="left", padx=10, pady=8)
            
            conf = f"{score*100:.1f}%"
            tk.Label(frame, text=f"置信度: {conf}", font=("微软雅黑", 10),
                    bg=bg, fg="#7f8c8d").pack(side="right", padx=10, pady=8)
            
            # 最高置信度结果高亮
            if i == 0:
                frame.configure(relief="raised", bd=2)
                best_name = name
                best_score = score
        
        # 如果有结果，显示提示
        if results:
            best_name = results[0][0]
            best_score = results[0][1]
            tk.Label(self.result_inner, text=f"最可能: {best_name} ({best_score*100:.1f}%)",
                    font=("微软雅黑", 9, "italic"), bg="#e8f5e9", fg="#27ae60",
                    relief="sunken").pack(fill="x", pady=(5,0))

    def clear(self):
        """清除内容"""
        self.current_screenshot = None
        self.img_label.configure(image="", text="未加载图片\n\n请按 F9 截图\n或点击下方按钮选择")
        self.img_label.image = None
        for widget in self.result_inner.winfo_children():
            widget.destroy()
        self.status_label.configure(text="状态: 就绪  |  按 F9 监听剪贴板截图")

    def run(self):
        """启动界面主循环"""
        self.root.mainloop()
