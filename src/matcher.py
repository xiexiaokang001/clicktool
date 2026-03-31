"""
图像模板匹配模块
使用 OpenCV 对截图与参考图库进行模板匹配
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Optional


class IconMatcher:
    def __init__(self, assets_dir: Path):
        self.assets_dir = Path(assets_dir)
        self.template_cache: dict[str, np.ndarray] = {}
        self._load_templates()

    def _load_templates(self):
        """加载所有参考图标到内存"""
        if not self.assets_dir.exists():
            raise FileNotFoundError(f"assets目录不存在: {self.assets_dir}")
        
        for img_path in self.assets_dir.glob("*.png"):
            name = img_path.stem  # 文件名（不含扩展名）作为门派名
            img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if img is not None:
                self.template_cache[name] = img
        
        if not self.template_cache:
            raise ValueError(f"assets目录为空: {self.assets_dir}")

    def match(self, screenshot: np.ndarray, threshold: float = 0.6) -> list[tuple[str, float]]:
        """
        将截图与所有参考图进行模板匹配
        
        Args:
            screenshot: 用户截图（OpenCV图像）
            threshold: 匹配置信度阈值，默认0.6
        
        Returns:
            按置信度排序的结果列表 [(门派名, 置信度), ...]
        """
        results = []
        
        for name, template in self.template_cache.items():
            try:
                # 尝试多种缩放比例找最佳匹配
                best_score = 0
                for scale in [0.8, 0.9, 1.0, 1.1, 1.2]:
                    h, w = template.shape[:2]
                    resized = cv2.resize(template, (int(w * scale), int(h * scale)))
                    
                    # 模板匹配
                    res = cv2.matchTemplate(screenshot, resized, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, _ = cv2.minMaxLoc(res)
                    
                    if max_val > best_score:
                        best_score = max_val
                
                if best_score >= threshold:
                    results.append((name, round(best_score, 3)))
                    
            except cv2.error:
                continue
        
        # 按置信度降序排列
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def match_best(self, screenshot: np.ndarray, threshold: float = 0.6) -> Optional[tuple[str, float]]:
        """返回置信度最高的匹配结果"""
        results = self.match(screenshot, threshold)
        return results[0] if results else None
