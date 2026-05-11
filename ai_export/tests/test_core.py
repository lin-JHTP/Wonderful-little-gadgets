import tempfile
import unittest
from pathlib import Path

from ai_export.core.detector import detect_format
from ai_export.core.file_writer import write_file


class DetectorTests(unittest.TestCase):
    def test_detect_json(self):
        result = detect_format('{"a":1}')
        self.assertEqual(result.extension, "json")

    def test_detect_yaml(self):
        result = detect_format("name: alice\nage: 18")
        self.assertEqual(result.extension, "yaml")

    def test_detect_code_to_markdown(self):
        result = detect_format("def hello():\n    return 1")
        self.assertEqual(result.extension, "md")
        self.assertTrue(result.is_code)


class WriterTests(unittest.TestCase):
    def test_write_json_pretty(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = write_file('{"a":1}', "demo", Path(tmp), detect_format('{"a":1}'))
            text = output.read_text(encoding="utf-8")
            self.assertIn('"a": 1', text)

    def test_write_markdown_with_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = write_file("hello", "标题", Path(tmp), detect_format("hello"))
            text = output.read_text(encoding="utf-8")
            self.assertIn("# 标题", text)
            self.assertIn("生成时间", text)


if __name__ == "__main__":
    unittest.main()
