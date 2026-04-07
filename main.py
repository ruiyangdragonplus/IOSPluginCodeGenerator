#!/usr/bin/env python3
"""
iOS Plugin File Generator - CLI 入口
流程编排：加载配置 → 初始化状态 → 生成命名 → 生成代码 → 写入文件
"""

import argparse
import os
import sys
from typing import Dict, Any, Optional

from core.config_loader import ConfigLoader
from core.state_store import StateStore
from core.name_builder import NameBuilder
from core.line_budget import LineBudget
from core.file_writer import FileWriter
from core.objc_generator import ObjCGenerator
from core.cpp_generator import CppGenerator
from core.string_generator import StringGenerator
from core.registry_generator import RegistryGenerator
from core.template_engine import TemplateEngine
from tools.line_counter import LineCounter, ReportGenerator


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="iOS Plugin File Generator - 批量生成 iOS 原生代码文件"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="./config/generator.json",
        help="配置文件路径 (默认：./config/generator.json)"
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=["objc", "cpp", "string"],
        help="覆盖配置中的语言选项"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="覆盖随机种子"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="覆盖输出目录"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    主函数
    
    Returns:
        退出码 (0=成功，1=失败)
    """
    args = parse_args()
    
    print("=" * 60)
    print("iOS Plugin File Generator")
    print("=" * 60)
    
    # 1. 加载配置
    print("\n[1/6] 加载配置文件...")
    try:
        config_loader = ConfigLoader(args.config)
        config = config_loader.load()
        
        # 应用命令行覆盖
        if args.language:
            config["language"] = args.language
        if args.seed is not None:
            config["randomSeed"] = args.seed
        if args.output:
            config["outputDir"] = args.output
        
        print(f"  语言：{config['language']}")
        print(f"  输出目录：{config['outputDir']}")
        if config["language"] == "string":
            print(f"  String 数量：{config.get('stringCount', 1000)}")
            print(f"  String 模式：{config.get('stringMode', 'word')}")
        else:
            print(f"  生成类数：{config['classCount']}")
            print(f"  总行数范围：{config['totalLineRange']}")
            print(f"  多样性级别：{config.get('diversityLevel', 'high')}")
    except Exception as e:
        print(f"  错误：{e}")
        return 1
    
    # 2. 加载词库
    print("\n[2/6] 加载词库配置...")
    try:
        vocabulary = ConfigLoader.load_vocabulary(config["vocabularyFile"])
        # 支持新旧词库格式
        custom_vocab = vocabulary.get("custom", vocabulary)
        builtin_vocab = vocabulary.get("builtin", {})
        print(f"  类名前缀词数：{len(custom_vocab.get('class', {}).get('prefix', []))}")
        print(f"  方法名动词数：{len(custom_vocab.get('method', {}).get('verb', []))}")
        print(f"  内置参数类型数：{len(builtin_vocab.get('paramType', {}).get('primitive', []))}")
        print(f"  内置返回类型数：{len(builtin_vocab.get('returnType', {}).get('primitive', []))}")
        print(f"  内置代码块类型数：{len(builtin_vocab.get('codeBlock', {}))}")
    except Exception as e:
        print(f"  错误：{e}")
        return 1
    
    # 3. 初始化状态存储
    print("\n[3/6] 初始化状态存储...")
    state_store = StateStore(config["stateFile"])
    state = state_store.load()
    print(f"  已使用类名数：{len(state.get('usedClassNames', []))}")
    print(f"  已使用方法名数：{len(state.get('usedMethodNames', []))}")
    print(f"  已生成文件数：{len(state.get('generatedFiles', []))}")
    
    # 4. 初始化命名构建器
    print("\n[4/6] 初始化命名构建器...")
    name_builder = NameBuilder(
        vocabulary=custom_vocab,
        state_store=state_store,
        class_prefix=config.get("classPrefix", "")
    )
    name_builder.set_seed(config.get("randomSeed", 12345))
    
    # 检查可用命名组合
    available_class_combos = name_builder.get_available_class_name_combos()
    available_method_combos = name_builder.get_available_method_name_combos()
    print(f"  可用类名组合：{available_class_combos}")
    print(f"  可用方法名组合：{available_method_combos}")
    
    if available_class_combos < config["classCount"]:
        print(f"  警告：可用类名组合不足，需要 {config['classCount']} 个，仅有 {available_class_combos} 个")
    
    # 5. 初始化行数预算
    print("\n[5/6] 分配行数预算...")
    line_budget = LineBudget(
        total_line_range=tuple(config["totalLineRange"]),
        lines_per_class_range=tuple(config["linesPerClassRange"]),
        methods_per_class_range=tuple(config["methodsPerClassRange"]),
        properties_per_class_range=tuple(config["propertiesPerClassRange"]),
        class_count=config["classCount"]
    )
    line_budget.set_seed(config.get("randomSeed", 12345))
    budgets = line_budget.allocate_budgets()
    total_allocated = line_budget.get_total_allocated()
    print(f"  已分配总行数：{total_allocated}")
    
    # 6. 初始化文件写入器
    print("\n[6/6] 初始化文件写入器...")
    file_writer = FileWriter(
        output_dir=config["outputDir"],
        overwrite=config.get("overwrite", False)
    )
    file_writer.ensure_output_dir()
    print(f"  输出目录：{file_writer.output_dir}")
    print(f"  覆盖模式：{'开启' if config.get('overwrite', False) else '关闭'}")
    
    # 7. 选择生成器并生成代码
    print(f"\n{'=' * 60}")
    print(f"开始生成 {config['language'].upper()} 代码...")
    print(f"{'=' * 60}")
    
    total_lines = 0
    generated_classes = []
    
    # 构建多样性配置
    diversity_config = {
        "diversityLevel": config.get("diversityLevel", "high"),
        "enableAsyncMethods": config.get("enableAsyncMethods", True),
        "enableBlockCallbacks": config.get("enableBlockCallbacks", True),
        "enableErrorHandling": config.get("enableErrorHandling", True),
        "enableGenericTypes": config.get("enableGenericTypes", True),
        "enableChainableMethods": config.get("enableChainableMethods", True),
        "enableFactoryMethods": config.get("enableFactoryMethods", True),
        "enableSingletonPattern": config.get("enableSingletonPattern", True),
        "enableDelegatePattern": config.get("enableDelegatePattern", True),
        "enableCacheLogic": config.get("enableCacheLogic", True),
        "enableValidationLogic": config.get("enableValidationLogic", True),
        "enableLoggingLogic": config.get("enableLoggingLogic", True)
    }
    
    if config["language"] == "string":
        # String 常量生成模式
        string_generator = StringGenerator(vocabulary=custom_vocab)
        string_generator.set_seed(config.get("randomSeed", 12345))
        
        string_count = config.get("stringCount", 1000)
        string_mode = config.get("stringMode", "word")
        
        print(f"\n生成 String 常量文件...")
        print(f"  String 数量：{string_count}")
        print(f"  String 模式：{string_mode}")
        
        # 生成文件
        file_info = string_generator.generate_file(
            string_count=string_count,
            language="objc" if config.get("stringLanguage", "objc") == "objc" else "cpp",
            mode=string_mode
        )
        
        # 写入文件
        result = file_writer.write_files([file_info])
        print(f"  写入文件：{result['written']}/{len([file_info])}")
        
        # 更新状态
        for f_info in [file_info]:
            file_path = os.path.join(file_writer.output_dir, f_info["filename"])
            state_store.mark_file_generated(file_path)
        
        # 统计行数
        total_lines += len(file_info["content"].split("\n"))
        generated_classes.append("ABStringConstants")
    else:
        # 原有的类生成模式 - 使用多样性配置初始化生成器
        if config["language"] == "objc":
            generator = ObjCGenerator(
                class_prefix=config.get("classPrefix", ""),
                vocabulary=vocabulary,
                diversity_config=diversity_config
            )
        else:
            generator = CppGenerator(
                class_prefix=config.get("classPrefix", ""),
                vocabulary=vocabulary,
                diversity_config=diversity_config
            )
        
        # 设置随机种子
        generator.set_seed(config.get("randomSeed", 12345))
        
        # 生成类
        for i, budget in enumerate(budgets):
            print(f"\n生成类 {i + 1}/{config['classCount']}...")
            
            # 生成类名
            class_name = name_builder.generate_class_name()
            if not class_name:
                print(f"  错误：无法生成唯一类名，跳过")
                continue
            
            print(f"  类名：{class_name}")
            print(f"  目标行数：{budget['target_lines']}")
            print(f"  方法数：{budget['methods_count']}")
            print(f"  属性数：{budget['properties_count']}")
            
            # 生成属性
            properties = []
            prop_names = name_builder.generate_property_names(budget["properties_count"])
            for prop_name in prop_names:
                prop_type = choose_property_type(name_builder, config["language"])
                properties.append({"name": prop_name, "type": prop_type})
            
            # 生成方法 - 使用模板引擎增加多样性
            methods = []
            method_names = name_builder.generate_method_names(budget["methods_count"])
            for idx, method_name in enumerate(method_names):
                return_type = choose_return_type(name_builder, vocabulary, config["language"])
                has_params = name_builder.random.random() > 0.5
                params = []
                if has_params:
                    param_count = name_builder.random.randint(1, 2)
                    for j in range(param_count):
                        params.append({
                            "name": f"param{j}",
                            "type": choose_param_type(name_builder, vocabulary, config["language"])
                        })
                
                # 使用模板引擎生成方法模板
                if diversity_config.get("diversityLevel", "high") == "high":
                    method_info = generator.generate_method_with_template(class_name, idx)
                    method_info["name"] = method_name  # 使用原有方法名
                    method_info["params"] = params
                    method_info["return_type"] = return_type
                    methods.append(method_info)
                else:
                    methods.append({
                        "name": method_name,
                        "return_type": return_type,
                        "params": params,
                        "complexity": line_budget.get_method_complexity(budget["lines_per_method"])
                    })
            
            # 生成文件
            if config["language"] == "objc":
                # 对于 ObjC，使用 properties 作为属性列表
                files = generator.generate_files(
                    class_name=class_name,
                    properties=properties,
                    methods=methods
                )
            else:
                # 对于 C++，使用 members 作为成员变量列表
                members = [{"name": p["name"], "type": p["type"]} for p in properties]
                files = generator.generate_files(
                    class_name=class_name,
                    members=members,
                    methods=methods
                )
            
            # 写入文件
            result = file_writer.write_files(files)
            print(f"  写入文件：{result['written']}/{len(files)}")
            
            # 更新状态
            for file_info in files:
                file_path = os.path.join(file_writer.output_dir, file_info["filename"])
                state_store.mark_file_generated(file_path)
            
            # 统计行数
            for file_info in files:
                total_lines += len(file_info["content"].split("\n"))
            
            generated_classes.append(class_name)
    
    # 8. 生成统一入口注册表（如果启用）
    if config.get("generateRegistry", False):
        print(f"\n{'=' * 60}")
        print("生成统一入口注册表...")
        
        registry_language = config.get("registryLanguage", "objc")
        print(f"  注册表语言：{registry_language}")
        
        # 增量生成：从状态文件获取所有已生成的类名，而不仅仅是当次生成的
        all_classes_for_registry = state_store.get_used_class_names()
        print(f"  注册表包含类数：{len(all_classes_for_registry)}")
        
        registry_generator = RegistryGenerator(class_prefix=config.get("classPrefix", "AB"))
        
        # 生成注册表实现文件
        registry_file = registry_generator.generate_registry(all_classes_for_registry, registry_language)
        # 注册表文件需要允许覆盖以支持增量更新
        result = file_writer.write_file(registry_file["filename"], registry_file["content"], check_exists=False)
        print(f"  写入注册表文件：{result}")
        
        # 生成注册表头文件
        header_file = registry_generator.generate_header_file(all_classes_for_registry)
        # 注册表头文件需要允许覆盖以支持增量更新
        result = file_writer.write_file(header_file["filename"], header_file["content"], check_exists=False)
        print(f"  写入头文件：{result}")
        
        # 将注册表文件记录到状态
        registry_path = os.path.join(file_writer.output_dir, registry_file["filename"])
        state_store.mark_file_generated(registry_path)
        header_path = os.path.join(file_writer.output_dir, header_file["filename"])
        state_store.mark_file_generated(header_path)
        
        print(f"  注册表生成完成!")
    
    # 9. 保存状态
    print(f"\n{'=' * 60}")
    print("保存状态...")
    state_store.add_history_entry({
        "language": config["language"],
        "generated_classes": generated_classes,
        "total_lines": total_lines,
        "files_written": len(file_writer.get_written_files()),
        "files_skipped": len(file_writer.get_skipped_files())
    })
    state_store.save()
    print(f"  状态已保存至：{config['stateFile']}")
    
    # 10. 输出摘要
    print(f"\n{'=' * 60}")
    print("生成完成!")
    print(f"{'=' * 60}")
    print(f"  语言：{config['language']}")
    print(f"  输出目录：{config['outputDir']}")
    print(f"  生成类数：{len(generated_classes)}")
    print(f"  生成文件数：{len(file_writer.get_written_files())}")
    print(f"  跳过文件数：{len(file_writer.get_skipped_files())}")
    print(f"  总行数：{total_lines}")
    print(f"  状态更新：是")
    
    # 打印文件列表
    file_writer.print_summary()
    
    # 显示行数统计报告
    show_stats = config.get("showStats", True)
    if show_stats:
        print(f"\n{'=' * 60}")
        print("代码生成完成 - 统计报告")
        print(f"{'=' * 60}")
        
        try:
            # 创建行数统计器
            counter = LineCounter(
                extensions=[".h", ".m", ".hpp", ".cpp"],
                exclude_patterns=[]
            )
            
            # 扫描输出目录
            from pathlib import Path
            target_dir = Path(config["outputDir"])
            counter.scan_directory(target_dir)
            
            # 计算汇总
            counter.calculate_summary()
            
            # 生成报告
            generator = ReportGenerator(counter, target_dir)
            print(generator.generate_text_report())
            
        except Exception as e:
            print(f"  警告：无法生成统计报告：{e}")
    
    return 0


def choose_property_type(name_builder: NameBuilder, language: str = "objc") -> str:
    """根据随机选择属性类型"""
    if language == "cpp":
        types = [
            "std::string",
            "int",
            "bool",
            "std::vector<void*>",
            "std::map<std::string, void*>",
            "int",
            "float",
            "double"
        ]
    else:
        types = [
            "NSString *",
            "NSInteger",
            "BOOL",
            "NSArray *",
            "NSDictionary *",
            "int",
            "float",
            "double"
        ]
    return name_builder.random.choice(types)


def choose_return_type(name_builder: NameBuilder, vocabulary: Optional[Dict[str, Any]] = None, language: str = "objc") -> str:
    """根据随机选择返回类型，支持从词库中选择"""
    if language == "cpp":
        # C++ 返回类型
        types = [
            "void",
            "void",
            "void",
            "int",
            "bool",
            "std::string",
            "int",
            "float"
        ]
        return name_builder.random.choice(types)
    
    # 如果提供了词库，从内置词库中选择
    if vocabulary:
        builtin = vocabulary.get("builtin", {})
        return_types = builtin.get("returnType", {})
        # 从不同类型中随机选择
        type_categories = ["primitive", "object", "optional", "errorHandling"]
        category = name_builder.random.choice(type_categories)
        if category in return_types and return_types[category]:
            return name_builder.random.choice(return_types[category])
    
    # 默认返回类型（Objective-C）
    types = [
        "void",
        "void",
        "void",
        "NSInteger",
        "BOOL",
        "NSString *",
        "int",
        "float"
    ]
    return name_builder.random.choice(types)


def choose_param_type(name_builder: NameBuilder, vocabulary: Optional[Dict[str, Any]] = None, language: str = "objc") -> str:
    """根据随机选择参数类型，支持从词库中选择"""
    if language == "cpp":
        # C++ 参数类型
        types = [
            "int",
            "std::string",
            "bool",
            "int",
            "float",
            "void*"
        ]
        return name_builder.random.choice(types)
    
    # 如果提供了词库，从内置词库中选择
    if vocabulary:
        builtin = vocabulary.get("builtin", {})
        param_types = builtin.get("paramType", {})
        # 从不同类型中随机选择
        type_categories = ["primitive", "object", "pointer"]
        category = name_builder.random.choice(type_categories)
        if category in param_types and param_types[category]:
            return name_builder.random.choice(param_types[category])
    
    # 默认参数类型（Objective-C）
    types = [
        "NSInteger",
        "NSString *",
        "BOOL",
        "int",
        "float",
        "id"
    ]
    return name_builder.random.choice(types)


if __name__ == "__main__":
    sys.exit(main())
