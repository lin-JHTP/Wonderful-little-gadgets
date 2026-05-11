"""核心模块导出。"""

from .detector import DetectionResult, detect_format
from .file_writer import write_file

__all__ = ["DetectionResult", "detect_format", "write_file"]
