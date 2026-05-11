# AI 内容文件生成器（插件化小工具箱）

这是一个基于 `tkinter + ttk` 的插件化小工具箱。

当前内置插件：**AI内容导出**，可将粘贴内容自动识别为合适格式并生成文件，方便上传给 AI。

## 如何运行

在 `ai_export/` 目录执行：

```bash
python main.py
```

## 如何打包为 exe

在 `ai_export/` 目录双击或执行：

```bat
build.bat
```

打包完成后，`exe` 位于 `dist` 目录。

## 如何新增插件

1. 在 `plugins/` 下新建一个 `.py` 文件
2. 继承 `BasePlugin`
3. 实现 `name` 和 `build_ui`
4. 重启程序后自动加载为新 Tab
