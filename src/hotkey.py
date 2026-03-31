"""
全局快捷键监听模块
使用 pynput 监听全局键盘事件，检测 F9 按键后自动获取剪贴板图片
"""
import io
import threading
from pynput import keyboard
from PIL import Image
import numpy as np
import cv2
import win32clipboard
from typing import Callable, Optional


class HotkeyListener:
    def __init__(self, hotkey: int = keyboard.Key.f9, callback: Optional[Callable[[np.ndarray], None]] = None):
        self.hotkey = hotkey
        self.callback = callback
        self.running = False
        self.listener: Optional[keyboard.Listener] = None
        
        # 用于线程安全
        self._lock = threading.Lock()

    def _get_clipboard_image(self) -> Optional[np.ndarray]:
        """从剪贴板获取图片"""
        try:
            win32clipboard.OpenClipboard()
            
            # 尝试获取 PNG 格式
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
                win32clipboard.CloseClipboard()
                
                # 解析 BMP DIB 数据 (DIB格式没有文件头)
                # DIB: [BITMAPINFOHEADER] + [pixel array]
                # 前40字节是BITMAPINFOHEADER
                import struct
                
                bih = data[:40]
                biSize, biWidth, biHeight, biPlanes, biBitCount = struct.unpack('<IiiHH', bih[0:20])
                
                # 处理BMP行序（倒序）和颜色通道
                # 通常 biHeight > 0 表示从上到下，< 0 表示从下到上
                rows = abs(biHeight)
                cols = biWidth
                
                if biBitCount == 32:
                    # BGRA 格式
                    pixel_data = data[40:]
                    img = np.frombuffer(pixel_data, dtype=np.uint8)
                    img = img.reshape((rows, cols, 4))
                    # 转为 BGR 并处理行序
                    if biHeight > 0:
                        img = img[::-1]
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    return img
                elif biBitCount == 24:
                    # BGR 格式
                    row_size = (cols * 3 + 3) & ~3
                    pixel_data = data[40:]
                    img = np.frombuffer(pixel_data, dtype=np.uint8)
                    img = img.reshape((rows, row_size))[:, :cols*3]
                    img = img.reshape((rows, cols, 3))
                    if biHeight > 0:
                        img = img[::-1]
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            
            win32clipboard.CloseClipboard()
            return None
            
        except Exception:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return None

    def _on_press(self, key):
        """按键回调"""
        if key == self.hotkey:
            with self._lock:
                if self.running and self.callback:
                    # 在新线程中处理，避免阻塞监听线程
                    threading.Thread(target=self._process_clipboard, daemon=True).start()

    def _process_clipboard(self):
        """处理剪贴板图片"""
        img_array = self._get_clipboard_image()
        if img_array is not None and self.callback:
            try:
                self.callback(img_array)
            except Exception as e:
                print(f"图片处理错误: {e}")
        else:
            print("剪贴板中未发现图片")

    def start(self):
        """启动监听"""
        with self._lock:
            if not self.running:
                self.running = True
                self.listener = keyboard.Listener(on_press=self._on_press)
                self.listener.daemon = True
                self.listener.start()

    def stop(self):
        """停止监听"""
        with self._lock:
            self.running = False
            if self.listener:
                self.listener.stop()
                self.listener = None

    def is_running(self) -> bool:
        with self._lock:
            return self.running
