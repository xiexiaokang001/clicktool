#!/usr/bin/env python3
"""
剑网三门派识别工具 - 入口文件

功能：
1. 启动时自动下载/更新门派图标
2. 监听全局快捷键 F9，检测剪贴板图片并自动识别
3. 提供图形界面，支持手动选择图片识别
"""
import sys
import argparse
from pathlib import Path

# 添加 src 目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.fetcher import IconFetcher
from src.gui import JX3DetectorGUI
from src.hotkey import HotkeyListener
from src.matcher import IconMatcher
import threading


def parse_args():
    parser = argparse.ArgumentParser(description="剑网三门派识别工具")
    parser.add_argument("--assets", "-a", type=str, default=None,
                       help="图标目录路径，默认为程序所在目录下的 assets/")
    parser.add_argument("--hotkey", "-k", type=str, default="f9",
                       help="全局快捷键，默认为 F9")
    parser.add_argument("--no-gui", action="store_true",
                       help="无界面模式（预留）")
    return parser.parse_args()


def main():
    args = parse_args()
    
    # 确定 assets 目录
    if args.assets:
        assets_dir = Path(args.assets)
    else:
        assets_dir = Path(__file__).parent / "assets"
    
    print("=" * 50)
    print("🎮 剑网三门派识别工具")
    print("=" * 50)
    
    # Step 1: 确保图标库就绪
    print(f"\n📦 图标库目录: {assets_dir}")
    fetcher = IconFetcher(assets_dir)
    
    local_count = fetcher.get_local_count()
    print(f"   已有的图标: {local_count} 个")
    
    if not fetcher.is_complete():
        print("\n⏬ 正在下载门派图标（首次运行）...")
        print("   (如下载失败，可手动将图标放入 assets/ 目录)\n")
        
        def progress(current, total, name):
            print(f"\r   [{current}/{total}] 正在下载: {name}...", end="", flush=True)
        
        results = fetcher.download_all(progress_callback=progress)
        print("\n\n   下载完成!")
        
        success_count = sum(1 for v in results.values() if v)
        print(f"   成功: {success_count}/{len(results)}")
        
        if success_count < len(results) * 0.5:
            print("\n⚠️ 警告: 下载成功率较低，请检查网络后重试")
            print("   或手动从网络获取图标放入 assets/ 目录")
    else:
        print("✅ 图标库已就绪")
    
    # Step 2: 验证 matcher
    try:
        matcher = IconMatcher(assets_dir)
        print(f"✅ 成功加载 {len(matcher.template_cache)} 个门派模板")
    except Exception as e:
        print(f"\n❌ 图标加载失败: {e}")
        print("   请确保 assets/ 目录包含 .png 图标文件")
        sys.exit(1)
    
    # Step 3: 启动 GUI
    print("\n🖥️ 启动图形界面...")
    print("   按 F9 从剪贴板获取图片并自动识别")
    print("   按 Ctrl+C 退出\n")
    
    gui = JX3DetectorGUI(assets_dir)
    
    # 绑定全局快捷键
    hotkey = HotkeyListener(callback=gui.set_screenshot)
    hotkey.start()
    print("✅ F9 全局快捷键已启用（剪贴板图片自动识别）")
    
    # 界面关闭时退出
    def on_close():
        hotkey.stop()
        gui.root.destroy()
    
    gui.root.protocol("WM_DELETE_WINDOW", on_close)
    
    try:
        gui.root.mainloop()
    except KeyboardInterrupt:
        print("\n\n👋 退出")
        hotkey.stop()
        sys.exit(0)


if __name__ == "__main__":
    main()
