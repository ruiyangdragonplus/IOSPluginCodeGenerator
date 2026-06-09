#!/usr/bin/env python3
"""
生产环境代码生成脚本
依次执行 4 种模式的代码生成：
1. OC 代码生成
2. C++ 代码生成
3. OC String 常量生成
4. C++ String 常量生成

生成逻辑统一在 core/orchestrator 中，本脚本只负责批量编排与统计输出。
"""

import argparse
import os
import sys
import time
from typing import Dict, Any

from core.config_loader import ConfigLoader
from core import orchestrator

# 向后兼容：保留模块级别名，供 tests / 外部脚本调用
generate_strings = orchestrator.generate_strings
choose_property_type = orchestrator.choose_property_type
choose_return_type = orchestrator.choose_return_type
choose_param_type = orchestrator.choose_param_type


def generate_code(config: Dict[str, Any], vocabulary: Dict[str, Any]) -> Dict[str, Any]:
    """生成整类代码（委托唯一编排实现，开启进度打印）。"""
    return orchestrator.generate_code(config, vocabulary, progress=True)


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_section(title: str) -> None:
    print(f"\n[{title}]")


def load_config(config_path: str) -> Dict[str, Any]:
    return ConfigLoader(config_path).load()


def load_vocabulary(vocab_path: str) -> Dict[str, Any]:
    return ConfigLoader.load_vocabulary(vocab_path)


def print_stats(mode_name: str, stats: Dict[str, Any]) -> None:
    print_section(f"{mode_name} 生成统计")
    print(f"  文件数：{stats.get('files', 0)}")
    print(f"  行数：{stats.get('lines', 0):,}")
    if 'classes' in stats:
        print(f"  类数：{stats.get('classes', 0)}")
    if 'strings' in stats:
        print(f"  String 数：{stats.get('strings', 0)}")
    print(f"  执行时间：{stats.get('execution_time', 0):.2f} 秒")


def main() -> int:
    parser = argparse.ArgumentParser(description="生产环境代码生成脚本")
    parser.add_argument("--oc", action="store_true", help="仅生成 OC 代码")
    parser.add_argument("--cpp", action="store_true", help="仅生成 C++ 代码")
    parser.add_argument("--string-oc", action="store_true", help="仅生成 OC String 常量")
    parser.add_argument("--string-cpp", action="store_true", help="仅生成 C++ String 常量")
    parser.add_argument("--config-dir", type=str, default="./config", help="配置文件目录")

    args = parser.parse_args()
    run_all = not (args.oc or args.cpp or args.string_oc or args.string_cpp)

    print_header("iOS Plugin Code Generator - 生产环境")
    print(f"配置目录：{args.config_dir}")

    all_stats: Dict[str, Any] = {}
    total_start_time = time.time()

    modes = [
        (run_all or args.oc, "模式 1: OC 代码生成", "generator_production_oc.json", "OC 代码", "code"),
        (run_all or args.cpp, "模式 2: C++ 代码生成", "generator_production_cpp.json", "C++ 代码", "code"),
        (run_all or args.string_oc, "模式 3: OC String 常量生成", "generator_production_string_oc.json", "OC String", "string"),
        (run_all or args.string_cpp, "模式 4: C++ String 常量生成", "generator_production_string_cpp.json", "C++ String", "string"),
    ]

    for enabled, header, config_name, label, kind in modes:
        if not enabled:
            continue
        print_header(header)
        config_path = os.path.join(args.config_dir, config_name)
        print(f"配置文件：{config_path}")
        try:
            config = load_config(config_path)
            vocabulary = load_vocabulary(config["vocabularyFile"])
            if kind == "code":
                stats = generate_code(config, vocabulary)
            else:
                stats = orchestrator.generate_strings(config, vocabulary)
            all_stats[label] = stats
            print_stats(label, stats)
        except Exception as e:
            print(f"  错误：{e}")
            return 1

    total_time = time.time() - total_start_time
    print_header("总统计")
    total_files = sum(s.get("files", 0) for s in all_stats.values())
    total_lines = sum(s.get("lines", 0) for s in all_stats.values())
    print(f"  总文件数：{total_files:,}")
    print(f"  总行数：{total_lines:,}")
    print(f"  总执行时间：{total_time:.2f} 秒")
    print("\n各模式统计:")
    for mode_name, stats in all_stats.items():
        print(f"  {mode_name}: {stats.get('files', 0)} 文件，"
              f"{stats.get('lines', 0):,} 行，{stats.get('execution_time', 0):.2f} 秒")
    print_header("生成完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
