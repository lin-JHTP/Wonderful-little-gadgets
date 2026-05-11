"""文件写入逻辑。"""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

from .detector import DetectionResult


def write_file(content: str, title: str, output_dir: Path, detection: DetectionResult) -> Path:
    """根据检测结果写入文件并返回文件路径。"""
    output_dir.mkdir(parents=True, exist_ok=True)

    safe_title = _safe_title(title)
    now = datetime.now()
    filename = f"{safe_title}_{now.strftime('%Y%m%d_%H%M%S')}.{detection.extension}"
    file_path = output_dir / filename

    final_content = _build_content(content, safe_title, now, detection)
    file_path.write_text(final_content, encoding="utf-8")
    return file_path


def _safe_title(title: str) -> str:
    raw = title.strip() or "ai_content"
    safe = re.sub(r"[\\/:*?\"<>|]+", "_", raw)
    safe = safe.strip("._ ")
    return safe or "ai_content"


def _build_content(content: str, title: str, now: datetime, detection: DetectionResult) -> str:
    body = content.strip()

    if detection.extension == "json":
        parsed = json.loads(body)
        return json.dumps(parsed, ensure_ascii=False, indent=2) + "\n"

    if detection.extension == "md":
        header = f"# {title}\n\n> 生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n"
        if detection.is_code:
            language = detection.language
            return f"{header}```{language}\n{body}\n```\n"
        return f"{header}{body}\n"

    return body + "\n"
