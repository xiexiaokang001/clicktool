"""
参考图下载模块
自动从网络下载剑网三所有心法图标
"""
import requests
from pathlib import Path
from typing import Optional
import time

# 剑网三全部心法列表（按门派分类）
# 格式：(心法英文名, 心法中文名, 可能的资源URL模式)
JIX3_MANTRAS = [
    # 门派
    ("qixiu", "花间游", "https://jx3.61.com/wp-content/uploads/icon/qixiu.png"),
    ("cangjian", "太虚剑意", "https://jx3.61.com/wp-content/uploads/icon/cangjian.png"),
    ("tiandou", "天宗剑意", "https://jx3.61.com/wp-content/uploads/icon/tiandou.png"),
    ("tianlu", "天罗诛心", "https://jx3.61.com/wp-content/uploads/icon/tianlu.png"),
    ("penglai", "蓬莱", "https://jx3.61.com/wp-content/uploads/icon/penglai.png"),
    ("changling", "长留", "https://jx3.61.com/wp-content/uploads/icon/changling.png"),
    ("xingyun", "星运", "https://jx3.61.com/wp-content/uploads/icon/xingyun.png"),
    ("badao", "傲血战意", "https://jx3.61.com/wp-content/uploads/icon/badao.png"),
    ("lingxu", "铁骨衣", "https://jx3.61.com/wp-content/uploads/icon/lingxu.png"),
    ("zhenwu", "分山劲", "https://jx3.61.com/wp-content/uploads/icon/zhenwu.png"),
    ("cuiyao", "山居剑意", "https://jx3.61.com/wp-content/uploads/icon/cuiyao.png"),
    ("mingdao", "明教", "https://jx3.61.com/wp-content/uploads/icon/mingdao.png"),
    ("wudu", "焚魔", "https://jx3.61.com/wp-content/uploads/icon/wudu.png"),
    ("tianchi", "冰心诀", "https://jx3.61.com/wp-content/uploads/icon/tianchi.png"),
    ("xueyue", "云裳", "https://jx3.61.com/wp-content/uploads/icon/xueyue.png"),
    ("shaolin", "易筋经", "https://jx3.61.com/wp-content/uploads/icon/shaolin.png"),
    ("shaolin_jy", "洗髓经", "https://jx3.61.com/wp-content/uploads/icon/shaolin_jy.png"),
    ("wanneng", "通用", "https://jx3.61.com/wp-content/uploads/icon/wanneng.png"),
]

# 备用资源站（FanSite sources）
FAN_SITES = [
    "https://raw.githubusercontent.com/JX3BOX/icon/main/move/{}.png",
    "https://raw.githubusercontent.com/JX3BOX/icon/main/class/{}.png",
]


class IconFetcher:
    def __init__(self, assets_dir: Path):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def download_all(self, progress_callback=None) -> dict[str, bool]:
        """
        下载所有心法图标
        返回：{心法名: 是否成功}
        """
        results = {}
        
        for i, (ename, cname, url) in enumerate(JIX3_MANTRAS):
            local_path = self.assets_dir / f"{ename}.png"
            
            if local_path.exists():
                results[cname] = True
                continue
            
            success = self._download_single(ename, url)
            results[cname] = success
            
            if progress_callback:
                progress_callback(i + 1, len(JIX3_MANTRAS), cname)
            
            time.sleep(0.3)  # 避免请求过快
        
        return results

    def _download_single(self, ename: str, url: str) -> bool:
        """尝试从主URL下载，失败则尝试备用资源站"""
        local_path = self.assets_dir / f"{ename}.png"
        
        for attempt_url in [url] + [site.format(ename) for site in FAN_SITES]:
            try:
                resp = self.session.get(attempt_url, timeout=10)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    local_path.write_bytes(resp.content)
                    return True
            except Exception:
                continue
        return False

    def get_local_count(self) -> int:
        """返回本地已有图标数量"""
        return len(list(self.assets_dir.glob("*.png")))

    def is_complete(self) -> bool:
        """检查是否已下载所有图标"""
        return self.get_local_count() >= len(JIX3_MANTRAS)
