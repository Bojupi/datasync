import json
import argparse
from pathlib import Path
from typing import Union


def parse_json(path: Union[Path, str]) -> dict:
    """载入JSON文件"""
    with open(path, mode='r') as f:
        return json.load(f)


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i", "--init_date",
        default="2010-01-01",
        metavar="",
        help="初始化日期（YYYY-MM-DD）（默认：2010-01-01）"
    )

    parser.add_argument(
        "-p","--path", 
        default='../db',
        metavar="",
        help="数据库构建目录（默认: ../db）"
    )

    return parser
