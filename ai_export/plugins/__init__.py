"""插件注册表：新增插件只需在此列表中添加即可。"""

from plugins.ai_export_plugin import AIExportPlugin

# 所有已注册的插件类，顺序即 Tab 顺序
ALL_PLUGINS = [
    AIExportPlugin,
]
