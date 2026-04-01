#!/usr/bin/env python3
"""下载剑网三心法图标（纯英文文件名，兼容 Windows）"""
import urllib.request
import os
from pathlib import Path

# 心法数据：ID -> (英文名, 中文名)
MANTRAS = {
    10026: ("aoxue", "傲血战意"),
    10062: ("tielao", "铁牢律"),
    10021: ("huajian", "花间游"),
    10028: ("lijing", "离经易道"),
    10014: ("zixia", "紫霞功"),
    10015: ("taixu", "太虚剑意"),
    10081: ("bingxin", "冰心诀"),
    10080: ("yunshang", "云裳心经"),
    10003: ("yijin", "易筋经"),
    10002: ("xisui", "洗髓经"),
    10144: ("wenshui", "问水诀"),
    10145: ("shanju", "山居剑意"),
    10268: ("xiaochen", "笑尘诀"),
    10242: ("fenying", "焚影圣诀"),
    10243: ("mingzun", "明尊琉璃体"),
    10175: ("dujing", "毒经"),
    10176: ("butian", "补天诀"),
    10224: ("jingyu", "惊羽诀"),
    10225: ("tianluo", "天罗诡道"),
    10389: ("tiegu", "铁骨衣"),
    10390: ("fenshan", "分山劲"),
    10447: ("mowen", "莫问"),
    10448: ("xiangzhi", "相知"),
    10464: ("beiao", "北傲诀"),
    10533: ("linghai", "凌海诀"),
    10585: ("yinlong", "隐龙诀"),
    10615: ("taixuan", "太玄经"),
    10626: ("lingsu", "灵素"),
    10627: ("wufang", "无方"),
    10698: ("gufeng", "孤锋诀"),
    10756: ("shanhai", "山海心诀"),
    10786: ("zhoutian", "周天功"),
    10821: ("youluo", "幽罗引"),
}

ICON_CDN = "https://icon.jx3box.com/icon"

def download():
    assets = Path("assets")
    assets.mkdir(exist_ok=True)
    
    headers = {"User-Agent": "Mozilla/5.0"}
    success = 0
    
    for icon_id, (ename, cname) in MANTRAS.items():
        filename = f"{ename}.png"
        filepath = assets / filename
        
        if filepath.exists() and filepath.stat().st_size > 100:
            print(f"  [跳过] {cname} ({ename}) 已存在")
            success += 1
            continue
        
        url = f"{ICON_CDN}/{icon_id}.png"
        print(f"  下载中: {cname} ({ename})...", end=" ", flush=True)
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if len(data) > 100:
                    filepath.write_bytes(data)
                    print("✓")
                    success += 1
                else:
                    print("✗ (文件太小)")
        except Exception as e:
            print(f"✗ ({e})")
    
    print(f"\n完成! 成功: {success}/{len(MANTRAS)}")
    print(f"图标目录: {assets.resolve()}")

if __name__ == "__main__":
    print("=" * 50)
    print("剑网三心法图标下载器")
    print("=" * 50)
    download()
