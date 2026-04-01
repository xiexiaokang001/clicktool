"""
心法图标下载模块
自动从网络下载剑网三所有心法图标
数据来源: https://github.com/JX3BOX/jx3box-data
图标CDN: https://icon.jx3box.com/icon/{id}.png
"""
import urllib.request
from pathlib import Path
import time
import json
import urllib.parse

# 剑网三全部心法列表（IconID -> 中文名）
# 数据来源: https://github.com/JX3BOX/jx3box-data/blob/master/data/xf/xf.json
# 仅保留正式服(std)心法，排除通用和怀旧服专属
JIX3_MANTRAS = {
    10026: "傲血战意",
    10062: "铁牢律",
    10021: "花间游",
    10028: "离经易道",
    10014: "紫霞功",
    10015: "太虚剑意",
    10081: "冰心诀",
    10080: "云裳心经",
    10003: "易筋经",
    10002: "洗髓经",
    10144: "问水诀",
    10145: "山居剑意",
    10268: "笑尘诀",
    10242: "焚影圣诀",
    10243: "明尊琉璃体",
    10175: "毒经",
    10176: "补天诀",
    10224: "惊羽诀",
    10225: "天罗诡道",
    10389: "铁骨衣",
    10390: "分山劲",
    10447: "莫问",
    10448: "相知",
    10464: "北傲诀",
    10533: "凌海诀",
    10585: "隐龙诀",
    10615: "太玄经",
    10626: "灵素",
    10627: "无方",
    10698: "孤锋诀",
    10756: "山海心诀",
    10786: "周天功",
    10821: "幽罗引",
}

# 图标CDN地址
ICON_CDN = "https://icon.jx3box.com/icon"


class IconFetcher:
    def __init__(self, assets_dir: Path):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def download_all(self, progress_callback=None) -> dict[str, bool]:
        """
        下载所有心法图标
        返回：{心法名: 是否成功}
        """
        results = {}
        items = list(JIX3_MANTRAS.items())
        
        for i, (icon_id, cname) in enumerate(items):
            local_path = self.assets_dir / f"{cname}.png"
            
            if local_path.exists() and local_path.stat().st_size > 100:
                results[cname] = True
                if progress_callback:
                    progress_callback(i + 1, len(items), cname)
                continue
            
            success = self._download_single(icon_id, cname)
            results[cname] = success
            
            if progress_callback:
                progress_callback(i + 1, len(items), cname)
            
            time.sleep(0.2)  # 避免请求过快
        
        return results

    def _download_single(self, icon_id: int, cname: str) -> bool:
        """从 icon.jx3box.com 下载单个图标"""
        local_path = self.assets_dir / f"{cname}.png"
        url = f"{ICON_CDN}/{icon_id}.png"
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                if len(data) > 100:
                    local_path.write_bytes(data)
                    return True
        except Exception:
            pass
        return False

    def get_local_count(self) -> int:
        """返回本地已有图标数量"""
        return len(list(self.assets_dir.glob("*.png")))

    def is_complete(self) -> bool:
        """检查是否已下载所有图标"""
        count = self.get_local_count()
        # 允许少量误差（可能有重名或缺失）
        return count >= len(JIX3_MANTRAS) * 0.9
