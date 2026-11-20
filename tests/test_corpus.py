"""交接资料格式和原文完整性测试。"""
from pathlib import Path
import json
import subprocess
import sys
import unittest

from corpus import read_collection

ROOT = Path(__file__).resolve().parents[1]


def records(name):
    return read_collection(ROOT / "data" / (name + ".json"))


class MaterialTests(unittest.TestCase):
    def test_collections_are_utf8_record_arrays(self):
        for name, fields in FIELDS.items():
            with self.subTest(collection=name):
                rows = records(name)
                self.assertTrue(rows)
                for row in rows:
                    self.assertEqual(set(row), set(fields))
                    self.assertIsInstance(row["id"], str)
                    self.assertTrue(row["id"])

    def test_reader_retains_exact_text_and_order(self):
        result = subprocess.check_output(
            [sys.executable, "-m", "corpus", PRIMARY, "--id", LINE_ID],
            cwd=ROOT, text=True, encoding="utf-8",
        )
        original = [row for row in records(PRIMARY) if row["id"] == LINE_ID]
        self.assertTrue(original)
        self.assertEqual(json.loads(result), original)

    def test_new_manuscript_version_retains_previous_bylines_and_invites(self):
        versions = [row["版次"] for row in records("submissions") if row["id"] == "M1"]
        self.assertEqual(versions, [1, 2])
        bylines = {(row["id"], row["版次"]) for row in records("bylines")}
        experts = {row["id"] for row in records("roster")}
        for item in records("desk"):
            self.assertIn((item["稿件"], item["版次"]), bylines)
            self.assertIn(item["专家"], experts)
        homonyms = [row for row in records("directory") if row["姓名"] == "何青"]
        self.assertEqual(len({row["单位"] for row in homonyms}), 2)


PRIMARY = 'submissions'
LINE_ID = 'M1'
FIELDS = {
    "submissions": [
        "id",
        "版次",
        "时间",
        "标题",
        "摘要",
        "贡献声明"
    ],
    "roster": [
        "id",
        "姓名",
        "单位",
        "分组",
        "专长声明",
        "回避声明",
        "名额"
    ],
    "directory": [
        "id",
        "姓名",
        "单位",
        "项目"
    ],
    "bylines": [
        "id",
        "版次",
        "人员",
        "署名单位"
    ],
    "desk": [
        "id",
        "稿件",
        "版次",
        "专家",
        "动作",
        "时间",
        "内容"
    ],
    "desk_rules": [
        "id",
        "原文"
    ]
}
