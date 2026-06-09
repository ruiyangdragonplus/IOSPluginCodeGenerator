#!/usr/bin/env python3
"""
iOS Plugin File Generator - CLI 入口
流程：加载配置 → 应用命令行覆盖并校验 → 委托 core.orchestrator 生成 → 统计报告

生成逻辑统一在 core/orchestrator，本入口只负责单配置运行与报告输出，
与 run_production.py 共用同一套生成实现（不再有分叉的生成循环）。
"""

import argparse
import sys
from pathlib import Path

from core.config_loader import ConfigLoader
from core import orchestrator
from tools.line_counter import LineCounter, ReportGenerator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="iOS Plugin File Generator - 批量生成 iOS 原生代码文件")
    parser.add_argument("--config", type=str, default="./config/generator.json",
                        help="配置文件路径 (默认：./config/generator.json)")
    parser.add_argument("--language", type=str, choices=["objc", "cpp", "string"],
                        help="覆盖配置中的语言选项")
    parser.add_argument("--seed", type=int, help="覆盖随机种子")
    parser.add_argument("--output", type=str, help="覆盖输出目录")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    print("=" * 60)
    print("iOS Plugin File Generator")
    print("=" * 60)

    # 1. 加载配置 + 命令行覆盖 + 重新校验
    print("\n[1/3] 加载配置文件...")
    try:
        loader = ConfigLoader(args.config)
        loader.load()
        overrides = {}
        if args.language:
            overrides["language"] = args.language
        if args.seed is not None:
            overrides["randomSeed"] = args.seed
        if args.output:
            overrides["outputDir"] = args.output
        if overrides:
            loader.override(overrides)
            loader._validate()  # 覆盖后重新校验，避免非法值绕过
        config = loader.config
        print(f"  语言：{config['language']}")
        print(f"  输出目录：{config['outputDir']}")
    except Exception as e:
        print(f"  错误：{e}")
        return 1

    # 2. 加载词库
    print("\n[2/3] 加载词库配置...")
    try:
        vocabulary = ConfigLoader.load_vocabulary(config["vocabularyFile"])
    except Exception as e:
        print(f"  错误：{e}")
        return 1

    # 3. 生成
    print("\n[3/3] 开始生成...")
    try:
        if config["language"] == "string":
            stats = orchestrator.generate_strings(config, vocabulary)
        else:
            stats = orchestrator.generate_code(config, vocabulary, progress=True)
    except Exception as e:
        print(f"  错误：{e}")
        return 1

    # 4. 摘要
    print("\n" + "=" * 60)
    print("生成完成!")
    print("=" * 60)
    print(f"  语言：{config['language']}")
    print(f"  输出目录：{config['outputDir']}")
    print(f"  文件数：{stats.get('files', 0)}")
    if 'classes' in stats:
        print(f"  类数：{stats.get('classes', 0)}")
    if 'strings' in stats:
        print(f"  String 数：{stats.get('strings', 0)}")
    print(f"  总行数：{stats.get('lines', 0):,}")
    print(f"  执行时间：{stats.get('execution_time', 0):.2f} 秒")

    # 5. 行数统计报告
    if config.get("showStats", True):
        print("\n" + "=" * 60)
        print("统计报告")
        print("=" * 60)
        try:
            counter = LineCounter(extensions=[".h", ".m", ".hpp", ".cpp"], exclude_patterns=[])
            target_dir = Path(config["outputDir"])
            counter.scan_directory(target_dir)
            counter.calculate_summary()
            print(ReportGenerator(counter, target_dir).generate_text_report())
        except Exception as e:
            print(f"  警告：无法生成统计报告：{e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
