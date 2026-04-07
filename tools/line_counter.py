#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码行数统计工具
用于统计目标文件夹中代码文件的行数信息
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class FileStats:
    """单个文件的统计信息"""
    path: str
    extension: str
    total_lines: int = 0
    code_lines: int = 0
    empty_lines: int = 0
    comment_lines: int = 0


@dataclass
class SummaryStats:
    """汇总统计信息"""
    total_files: int = 0
    files_by_extension: Dict[str, int] = field(default_factory=dict)
    total_lines: int = 0
    code_lines: int = 0
    empty_lines: int = 0
    comment_lines: int = 0


class LineCounter:
    """代码行数统计器"""
    
    # C/C++/Objective-C 注释模式
    SINGLE_LINE_COMMENT = re.compile(r'^\s*//')
    BLOCK_COMMENT_START = re.compile(r'/\*')
    BLOCK_COMMENT_END = re.compile(r'\*/')
    
    def __init__(self, extensions: List[str], exclude_patterns: List[str]):
        self.extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                          for ext in extensions]
        self.exclude_patterns = exclude_patterns
        self.file_stats: List[FileStats] = []
        self.summary = SummaryStats()
    
    def should_exclude(self, path: Path) -> bool:
        """检查路径是否应该被排除"""
        path_str = str(path).lower()
        for pattern in self.exclude_patterns:
            if pattern.lower() in path_str:
                return True
        return False
    
    def is_target_file(self, path: Path) -> bool:
        """检查文件是否是目标文件"""
        return path.suffix.lower() in self.extensions
    
    def count_lines(self, file_path: Path) -> FileStats:
        """统计单个文件的行数"""
        stats = FileStats(
            path=str(file_path),
            extension=file_path.suffix.lower()
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except (IOError, OSError) as e:
            print(f"警告：无法读取文件 {file_path}: {e}", file=sys.stderr)
            return stats
        
        stats.total_lines = len(lines)
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            # 空行判断
            if not stripped:
                stats.empty_lines += 1
                continue
            
            # 注释判断
            is_comment = False
            
            # 处理块注释
            if in_block_comment:
                is_comment = True
                if self.BLOCK_COMMENT_END.search(stripped):
                    in_block_comment = False
            else:
                # 单行注释
                if self.SINGLE_LINE_COMMENT.match(stripped):
                    is_comment = True
                # 块注释开始
                elif self.BLOCK_COMMENT_START.search(stripped):
                    is_comment = True
                    if not self.BLOCK_COMMENT_END.search(stripped):
                        in_block_comment = True
            
            if is_comment:
                stats.comment_lines += 1
            else:
                stats.code_lines += 1
        
        return stats
    
    def scan_directory(self, target_dir: Path) -> None:
        """扫描目录并统计所有目标文件"""
        if not target_dir.exists():
            raise FileNotFoundError(f"目录不存在：{target_dir}")
        
        if not target_dir.is_dir():
            raise NotADirectoryError(f"不是目录：{target_dir}")
        
        for root, dirs, files in os.walk(target_dir):
            root_path = Path(root)
            
            # 过滤排除的目录
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]
            
            for filename in files:
                file_path = root_path / filename
                
                if self.should_exclude(file_path):
                    continue
                
                if self.is_target_file(file_path):
                    stats = self.count_lines(file_path)
                    self.file_stats.append(stats)
    
    def calculate_summary(self) -> SummaryStats:
        """计算汇总统计"""
        self.summary = SummaryStats()
        self.summary.total_files = len(self.file_stats)
        
        files_by_ext: Dict[str, int] = defaultdict(int)
        
        for stats in self.file_stats:
            files_by_ext[stats.extension] += 1
            self.summary.total_lines += stats.total_lines
            self.summary.code_lines += stats.code_lines
            self.summary.empty_lines += stats.empty_lines
            self.summary.comment_lines += stats.comment_lines
        
        self.summary.files_by_extension = dict(files_by_ext)
        return self.summary
    
    def get_top_files(self, n: int = 10) -> List[FileStats]:
        """获取最大的 N 个文件"""
        sorted_files = sorted(self.file_stats, 
                             key=lambda x: x.total_lines, 
                             reverse=True)
        return sorted_files[:n]


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, counter: LineCounter, target_dir: Path):
        self.counter = counter
        self.target_dir = target_dir
    
    def generate_text_report(self) -> str:
        """生成文本格式报告"""
        lines = []
        separator = "=" * 40
        
        lines.append(separator)
        lines.append("代码行数统计报告")
        lines.append(separator)
        lines.append(f"目标目录：{self.target_dir}")
        lines.append("")
        
        # 文件统计
        lines.append("文件统计:")
        lines.append(f"  总文件数：{self.counter.summary.total_files}")
        for ext, count in sorted(self.counter.summary.files_by_extension.items()):
            lines.append(f"  {ext} 文件：{count}")
        lines.append("")
        
        # 行数统计
        lines.append("行数统计:")
        lines.append(f"  总行数：{self.counter.summary.total_lines}")
        lines.append(f"  代码行数：{self.counter.summary.code_lines}")
        lines.append(f"  空行数：{self.counter.summary.empty_lines}")
        lines.append(f"  注释行数：{self.counter.summary.comment_lines}")
        lines.append("")
        
        # Top 10 最大文件
        top_files = self.counter.get_top_files(10)
        if top_files:
            lines.append("Top 10 最大文件:")
            for i, stats in enumerate(top_files, 1):
                filename = os.path.basename(stats.path)
                lines.append(f"  {i}. {filename} - {stats.total_lines} 行")
            lines.append("")
        
        # 按扩展名汇总
        lines.append("按扩展名汇总:")
        ext_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'files': 0, 'total': 0, 'code': 0, 'empty': 0, 'comment': 0
        })
        
        for stats in self.counter.file_stats:
            ext = stats.extension
            ext_stats[ext]['files'] += 1
            ext_stats[ext]['total'] += stats.total_lines
            ext_stats[ext]['code'] += stats.code_lines
            ext_stats[ext]['empty'] += stats.empty_lines
            ext_stats[ext]['comment'] += stats.comment_lines
        
        for ext in sorted(ext_stats.keys()):
            stats = ext_stats[ext]
            lines.append(f"  {ext}:")
            lines.append(f"    文件数：{stats['files']}")
            lines.append(f"    总行数：{stats['total']}")
            lines.append(f"    代码行数：{stats['code']}")
            lines.append(f"    空行数：{stats['empty']}")
            lines.append(f"    注释行数：{stats['comment']}")
        
        lines.append("")
        lines.append(separator)
        
        return "\n".join(lines)
    
    def generate_json_report(self) -> str:
        """生成 JSON 格式报告"""
        report = {
            "target_directory": str(self.target_dir),
            "file_statistics": {
                "total_files": self.counter.summary.total_files,
                "files_by_extension": self.counter.summary.files_by_extension
            },
            "line_statistics": {
                "total_lines": self.counter.summary.total_lines,
                "code_lines": self.counter.summary.code_lines,
                "empty_lines": self.counter.summary.empty_lines,
                "comment_lines": self.counter.summary.comment_lines
            },
            "top_files": [
                {
                    "filename": os.path.basename(stats.path),
                    "path": stats.path,
                    "extension": stats.extension,
                    "total_lines": stats.total_lines,
                    "code_lines": stats.code_lines,
                    "empty_lines": stats.empty_lines,
                    "comment_lines": stats.comment_lines
                }
                for stats in self.counter.get_top_files(10)
            ],
            "by_extension": {}
        }
        
        # 按扩展名汇总
        ext_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {
            'files': 0, 'total': 0, 'code': 0, 'empty': 0, 'comment': 0
        })
        
        for stats in self.counter.file_stats:
            ext = stats.extension
            ext_stats[ext]['files'] += 1
            ext_stats[ext]['total'] += stats.total_lines
            ext_stats[ext]['code'] += stats.code_lines
            ext_stats[ext]['empty'] += stats.empty_lines
            ext_stats[ext]['comment'] += stats.comment_lines
        
        report["by_extension"] = dict(ext_stats)
        
        return json.dumps(report, indent=2, ensure_ascii=False)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="代码行数统计工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python line_counter.py ./output_1m_test
  python line_counter.py ./src --extensions .h,.m,.cpp
  python line_counter.py ./src --output json
  python line_counter.py ./src --exclude build,dist,node_modules
        """
    )
    
    parser.add_argument(
        "target_dir",
        type=str,
        help="目标文件夹路径"
    )
    
    parser.add_argument(
        "--extensions",
        type=str,
        default=".h,.m,.hpp,.cpp",
        help="要统计的文件扩展名，逗号分隔 (默认：.h,.m,.hpp,.cpp)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="输出格式 (默认：text)"
    )
    
    parser.add_argument(
        "--exclude",
        type=str,
        default="",
        help="排除的文件夹模式，逗号分隔 (例如：build,dist,node_modules)"
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 解析扩展名
    extensions = [ext.strip() for ext in args.extensions.split(",") if ext.strip()]
    
    # 解析排除模式
    exclude_patterns = [p.strip() for p in args.exclude.split(",") if p.strip()]
    
    # 目标目录
    target_dir = Path(args.target_dir)
    
    try:
        # 创建统计器
        counter = LineCounter(extensions, exclude_patterns)
        
        # 扫描目录
        print(f"正在扫描目录：{target_dir}", file=sys.stderr)
        counter.scan_directory(target_dir)
        
        # 计算汇总
        counter.calculate_summary()
        
        # 生成报告
        generator = ReportGenerator(counter, target_dir)
        
        if args.output == "json":
            print(generator.generate_json_report())
        else:
            print(generator.generate_text_report())
        
    except FileNotFoundError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)
    except NotADirectoryError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
