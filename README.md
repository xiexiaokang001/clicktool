# 剑网三门派识别工具

通过游戏界面截图，自动识别玩家门派/心法。

## 功能

- 🎯 **F9 全局快捷键**：截取游戏画面后，直接按 F9 即可自动识别
- 🖼️ **剪贴板直读**：自动获取剪贴板图片，无需手动选择文件
- 📊 **置信度排序**：显示所有可能的匹配结果，按置信度排列
- 📦 **自动下载图标**：首次运行自动从网络获取全部门派图标
- 🖥️ **轻量 GUI**：Tkinter 编写，Windows 解压即用

## 使用方法

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行

```bash
python main.py
```

### 3. 识别步骤

1. 用截图工具（微信截图、QQ截图、Win+Shift+S 等）截取游戏界面中的门派图标
2. 按 **F9**，工具自动读取剪贴板图片并识别
3. 查看识别结果

## 目录结构

```
clicktool/
├── main.py              # 入口
├── src/
│   ├── fetcher.py       # 图标下载
│   ├── matcher.py       # 图像匹配
│   ├── gui.py           # 图形界面
│   └── hotkey.py        # 全局快捷键
├── assets/              # 门派图标库（自动下载）
└── requirements.txt     # Python 依赖
```

## 打包为 Windows EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "JX3Detector" main.py
```

生成的文件在 `dist/` 目录下，可直接拷贝到其他 Windows 机器运行。

## 技术栈

- Python 3.10+
- OpenCV（图像模板匹配）
- Tkinter（图形界面）
- pynput（全局键盘监听）
- PyInstaller（打包）
