"""格式自动检测逻辑。"""

from dataclasses import dataclass
import json
import re


@dataclass
class DetectionResult:
    """内容检测结果。"""

    extension: str
    format_label: str
    is_code: bool = False
    language: str = ""


def detect_format(content: str) -> DetectionResult:
    """按优先级检测内容适合导出的格式。"""
    text = content.strip()

    if _is_json(text):
        return DetectionResult(extension="json", format_label="JSON")

    if _is_yaml(text):
        return DetectionResult(extension="yaml", format_label="YAML")

    if _is_code(text):
        return DetectionResult(
            extension="md",
            format_label="Markdown（代码块）",
            is_code=True,
            language=_guess_language(text),
        )

    if _is_markdown(text):
        return DetectionResult(extension="md", format_label="Markdown")

    if _is_csv(text):
        return DetectionResult(extension="csv", format_label="CSV")

    return DetectionResult(extension="md", format_label="Markdown")


def _is_json(text: str) -> bool:
    if not text:
        return False
    try:
        json.loads(text)
    except Exception:
        return False
    return True


def _is_yaml(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return False

    pattern = re.compile(r"^[\w\-\.\"']+\s*:\s*.+$")
    matched = [line for line in lines if pattern.match(line)]
    return len(matched) >= 2


def _is_code(text: str) -> bool:
    keywords = [
        "def ",
        "function ",
        "#include",
        "class ",
        "import ",
        "const ",
        "let ",
        "var ",
        "public static",
    ]
    return any(keyword in text for keyword in keywords)


def _is_markdown(text: str) -> bool:
    patterns = [
        r"^#{1,6}\s+",
        r"^\s*[-*+]\s+",
        r"\*\*.+\*\*",
        r"```",
    ]
    return any(re.search(pattern, text, flags=re.MULTILINE) for pattern in patterns)


def _is_csv(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if len(lines) < 2:
        return False

    counts = [line.count(",") + 1 for line in lines[:5]]
    return min(counts) >= 2 and len(set(counts)) == 1


def _guess_language(text: str) -> str:
    mapping = {
        "#include": "cpp",
        "def ": "python",
        "import ": "python",
        "function ": "javascript",
        "const ": "javascript",
        "let ": "javascript",
        "var ": "javascript",
        "public static": "java",
        "class ": "python",
    }
    for keyword, lang in mapping.items():
        if keyword in text:
            return lang
    return ""
