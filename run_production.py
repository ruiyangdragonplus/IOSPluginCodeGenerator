#!/usr/bin/env python3
"""
生产环境代码生成脚本
依次执行 4 种模式的代码生成：
1. OC 代码生成
2. C++ 代码生成
3. OC String 常量生成
4. C++ String 常量生成
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
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
from tools.line_counter import LineCounter, ReportGenerator


def print_header(title: str) -> None:
    """打印标题"""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_section(title: str) -> None:
    """打印小标题"""
    print(f"\n[{title}]")


def load_config(config_path: str) -> Dict[str, Any]:
    """加载配置文件"""
    config_loader = ConfigLoader(config_path)
    config = config_loader.load()
    return config


def load_vocabulary(vocab_path: str) -> Dict[str, Any]:
    """加载词库"""
    return ConfigLoader.load_vocabulary(vocab_path)


def generate_code(config: Dict[str, Any], vocabulary: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成代码文件
    
    Returns:
        生成统计信息
    """
    stats = {
        "files": 0,
        "lines": 0,
        "classes": 0,
        "execution_time": 0
    }
    
    start_time = time.time()
    
    # 初始化状态存储
    state_store = StateStore(config["stateFile"])
    state = state_store.load()
    
    # 初始化命名构建器
    name_builder = NameBuilder(
        vocabulary=vocabulary.get("custom", vocabulary),
        state_store=state_store,
        class_prefix=config.get("classPrefix", "")
    )
    name_builder.set_seed(config.get("randomSeed", 12345))
    
    # 初始化行数预算
    line_budget = LineBudget(
        total_line_range=tuple(config["totalLineRange"]),
        lines_per_class_range=tuple(config["linesPerClassRange"]),
        methods_per_class_range=tuple(config["methodsPerClassRange"]),
        properties_per_class_range=tuple(config["propertiesPerClassRange"]),
        class_count=config["classCount"]
    )
    line_budget.set_seed(config.get("randomSeed", 12345))
    budgets = line_budget.allocate_budgets()
    
    # 初始化文件写入器
    file_writer = FileWriter(
        output_dir=config["outputDir"],
        overwrite=config.get("overwrite", False)
    )
    file_writer.ensure_output_dir()
    
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
    
    # 选择生成器
    language = config["language"]
    if language == "objc":
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
    
    generator.set_seed(config.get("randomSeed", 12345))
    
    total_lines = 0
    generated_classes = []
    
    # 生成类
    for i, budget in enumerate(budgets):
        # 生成类名
        class_name = name_builder.generate_class_name()
        if not class_name:
            print(f"  警告：无法生成唯一类名，跳过第 {i + 1} 个类")
            continue
        
        # 生成属性
        properties = []
        prop_names = name_builder.generate_property_names(budget["properties_count"])
        for prop_name in prop_names:
            prop_type = choose_property_type(name_builder, language)
            properties.append({"name": prop_name, "type": prop_type})
        
        # 生成方法
        methods = []
        method_names = name_builder.generate_method_names(budget["methods_count"])
        used_method_names = set()  # 跟踪已使用的方法名，避免重复
        
        for idx in range(budget["methods_count"]):
            # 使用模板引擎生成方法模板
            if diversity_config.get("diversityLevel", "high") == "high":
                method_info = generator.generate_method_with_template(class_name, idx)
                # 使用模板生成的方法名（模板可能包含固定名称如 sharedInstance）
                # 如果模板没有固定名称，则使用随机生成的方法名
                template = method_info.get("template", {})
                signature_format = template.get("signature_format", "")
                
                # 检查模板是否有固定的方法名（如 sharedInstance）
                if "sharedInstance" in signature_format or "createInstance" in signature_format:
                    # 使用模板的固定方法名，但需要确保唯一性
                    method_name = method_info["name"]
                    # 如果方法名已存在，跳过这个模板方法（不添加重复的方法）
                    if method_name in used_method_names:
                        # 使用随机生成的方法名替代
                        method_name = method_names[idx] if idx < len(method_names) else f"method{idx}"
                        base_name = method_name
                        counter = 0
                        while method_name in used_method_names:
                            counter += 1
                            method_name = f"{base_name}{counter}"
                        used_method_names.add(method_name)
                        method_info["name"] = method_name
                    else:
                        used_method_names.add(method_name)
                else:
                    # 使用随机生成的方法名，确保唯一性
                    method_name = method_names[idx] if idx < len(method_names) else f"method{idx}"
                    # 确保方法名唯一
                    base_name = method_name
                    counter = 0
                    while method_name in used_method_names:
                        counter += 1
                        method_name = f"{base_name}{counter}"
                    used_method_names.add(method_name)
                    method_info["name"] = method_name
                
                # 生成参数（如果模板没有定义参数）
                template_params = method_info.get("params", [])
                if not template_params:
                    has_params = name_builder.random.random() > 0.5
                    params = []
                    if has_params:
                        param_count = name_builder.random.randint(1, 2)
                        for j in range(param_count):
                            params.append({
                                "name": f"param{j}",
                                "type": choose_param_type(name_builder, vocabulary, language)
                            })
                    method_info["params"] = params
                
                # 设置返回类型（如果模板没有定义）
                # 注意：generate_method_with_template 已经从模板签名中提取了返回类型
                # 只有当返回类型确实为空时才设置默认值
                if not method_info.get("return_type") or method_info["return_type"] == "void":
                    # 检查模板是否有固定的返回类型（如 instancetype）
                    template = method_info.get("template", {})
                    signature_format = template.get("signature_format", "")
                    if signature_format:
                        # 从签名中提取返回类型
                        import re
                        return_type_match = re.search(r'[\+\-]\s*\(([^)]+)\)', signature_format)
                        if return_type_match:
                            extracted_type = return_type_match.group(1).strip()
                            if extracted_type not in ["void"]:
                                method_info["return_type"] = extracted_type
                            else:
                                method_info["return_type"] = choose_return_type(name_builder, vocabulary, language)
                        else:
                            method_info["return_type"] = choose_return_type(name_builder, vocabulary, language)
                    else:
                        method_info["return_type"] = choose_return_type(name_builder, vocabulary, language)
                
                methods.append(method_info)
            else:
                method_name = method_names[idx] if idx < len(method_names) else f"method{idx}"
                # 确保方法名唯一
                base_name = method_name
                counter = 0
                while method_name in used_method_names:
                    counter += 1
                    method_name = f"{base_name}{counter}"
                used_method_names.add(method_name)
                
                return_type = choose_return_type(name_builder, vocabulary, language)
                has_params = name_builder.random.random() > 0.5
                params = []
                if has_params:
                    param_count = name_builder.random.randint(1, 2)
                    for j in range(param_count):
                        params.append({
                            "name": f"param{j}",
                            "type": choose_param_type(name_builder, vocabulary, language)
                        })
                
                methods.append({
                    "name": method_name,
                    "return_type": return_type,
                    "params": params,
                    "complexity": line_budget.get_method_complexity(budget["lines_per_method"])
                })
        
        # 生成文件
        if language == "objc":
            files = generator.generate_files(
                class_name=class_name,
                properties=properties,
                methods=methods
            )
        else:
            members = [{"name": p["name"], "type": p["type"]} for p in properties]
            files = generator.generate_files(
                class_name=class_name,
                members=members,
                methods=methods
            )
        
        # 写入文件
        result = file_writer.write_files(files)
        
        # 更新状态
        for file_info in files:
            file_path = os.path.join(file_writer.output_dir, file_info["filename"])
            state_store.mark_file_generated(file_path)
        
        # 统计行数
        for file_info in files:
            total_lines += len(file_info["content"].split("\n"))
        
        generated_classes.append(class_name)
        stats["files"] += len(files)
        stats["classes"] += 1
        
        # 每生成 100 个类显示一次进度
        if (i + 1) % 100 == 0:
            print(f"  进度：{i + 1}/{config['classCount']} 类，已生成 {total_lines} 行")
    
    # 生成注册表（如果启用）
    if config.get("generateRegistry", False):
        print_section("生成统一入口注册表")
        
        registry_language = config.get("registryLanguage", language)
        all_classes_for_registry = state_store.get_used_class_names()
        
        registry_generator = RegistryGenerator(class_prefix=config.get("classPrefix", "MX11"))
        
        # 生成注册表实现文件
        registry_file = registry_generator.generate_registry(all_classes_for_registry, registry_language)
        result = file_writer.write_file(registry_file["filename"], registry_file["content"], check_exists=False)
        
        # 生成注册表头文件（传递语言参数）
        header_file = registry_generator.generate_header_file(all_classes_for_registry, registry_language)
        result = file_writer.write_file(header_file["filename"], header_file["content"], check_exists=False)
        
        # 记录到状态
        registry_path = os.path.join(file_writer.output_dir, registry_file["filename"])
        state_store.mark_file_generated(registry_path)
        header_path = os.path.join(file_writer.output_dir, header_file["filename"])
        state_store.mark_file_generated(header_path)
        
        stats["files"] += 2
    
    # 保存状态
    state_store.add_history_entry({
        "language": language,
        "generated_classes": generated_classes,
        "total_lines": total_lines,
        "files_written": len(file_writer.get_written_files()),
        "files_skipped": len(file_writer.get_skipped_files())
    })
    state_store.save()
    
    stats["lines"] = total_lines
    stats["execution_time"] = time.time() - start_time
    
    return stats


def generate_strings(config: Dict[str, Any], vocabulary: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成 String 常量文件
    
    Returns:
        生成统计信息
    """
    import json
    
    stats = {
        "files": 0,
        "lines": 0,
        "strings": 0,
        "execution_time": 0
    }
    
    start_time = time.time()
    
    # 初始化状态存储
    state_store = StateStore(config["stateFile"])
    state = state_store.load()
    
    # 初始化 String 生成器
    string_generator = StringGenerator(vocabulary=vocabulary.get("custom", vocabulary))
    string_generator.set_seed(config.get("randomSeed", 12345))
    
    string_count = config.get("stringCount", 5000)
    string_mode = config.get("stringMode", "word")
    string_language = config.get("stringLanguage", "objc")
    output_filename = config.get("outputFileName", "MX11StringConstants")
    
    # 初始化文件写入器
    file_writer = FileWriter(
        output_dir=config["outputDir"],
        overwrite=config.get("overwrite", False)
    )
    file_writer.ensure_output_dir()
    
    print(f"  String 数量：{string_count}")
    print(f"  String 模式：{string_mode}")
    print(f"  目标语言：{string_language}")
    print(f"  输出文件名：{output_filename}")
    
    # 生成文件
    file_info = string_generator.generate_file(
        string_count=string_count,
        language=string_language,
        mode=string_mode,
        prefix="MX11",
        output_filename=output_filename
    )
    
    # 写入文件
    result = file_writer.write_files([file_info])
    
    # 更新状态
    file_path = os.path.join(file_writer.output_dir, file_info["filename"])
    state_store.mark_file_generated(file_path)
    state_store.save()
    
    stats["files"] = result["written"]
    stats["lines"] = len(file_info["content"].split("\n"))
    stats["strings"] = string_count
    stats["execution_time"] = time.time() - start_time
    
    # 保存统计信息到 JSON 文件
    stats_file_path = os.path.join(config["outputDir"], "generation_stats.json")
    stats_data = {
        "string_count": string_count,
        "file_lines": stats["lines"],
        "execution_time": stats["execution_time"],
        "output_file": file_info["filename"],
        "mode": string_mode,
        "language": string_language
    }
    with open(stats_file_path, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2)
    
    return stats


def print_stats(mode_name: str, stats: Dict[str, Any]) -> None:
    """打印生成统计"""
    print_section(f"{mode_name} 生成统计")
    print(f"  文件数：{stats.get('files', 0)}")
    print(f"  行数：{stats.get('lines', 0):,}")
    if 'classes' in stats:
        print(f"  类数：{stats.get('classes', 0)}")
    if 'strings' in stats:
        print(f"  String 数：{stats.get('strings', 0)}")
    print(f"  执行时间：{stats.get('execution_time', 0):.2f} 秒")


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
    """根据随机选择返回类型"""
    if language == "cpp":
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
    
    if vocabulary:
        builtin = vocabulary.get("builtin", {})
        return_types = builtin.get("returnType", {})
        type_categories = ["primitive", "object", "optional", "errorHandling"]
        category = name_builder.random.choice(type_categories)
        if category in return_types and return_types[category]:
            return name_builder.random.choice(return_types[category])
    
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
    """根据随机选择参数类型"""
    if language == "cpp":
        types = [
            "int",
            "std::string",
            "bool",
            "int",
            "float",
            "void*"
        ]
        return name_builder.random.choice(types)
    
    if vocabulary:
        builtin = vocabulary.get("builtin", {})
        param_types = builtin.get("paramType", {})
        type_categories = ["primitive", "object", "pointer"]
        category = name_builder.random.choice(type_categories)
        if category in param_types and param_types[category]:
            return name_builder.random.choice(param_types[category])
    
    types = [
        "NSInteger",
        "NSString *",
        "BOOL",
        "int",
        "float",
        "id"
    ]
    return name_builder.random.choice(types)


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description="生产环境代码生成脚本")
    parser.add_argument("--oc", action="store_true", help="仅生成 OC 代码")
    parser.add_argument("--cpp", action="store_true", help="仅生成 C++ 代码")
    parser.add_argument("--string-oc", action="store_true", help="仅生成 OC String 常量")
    parser.add_argument("--string-cpp", action="store_true", help="仅生成 C++ String 常量")
    parser.add_argument("--config-dir", type=str, default="./config", help="配置文件目录")
    
    args = parser.parse_args()
    
    # 如果没有指定任何模式，则执行所有模式
    run_all = not (args.oc or args.cpp or args.string_oc or args.string_cpp)
    
    print_header("iOS Plugin Code Generator - 生产环境")
    print(f"配置目录：{args.config_dir}")
    
    all_stats = {}
    total_start_time = time.time()
    
    # 1. OC 代码生成
    if run_all or args.oc:
        print_header("模式 1: OC 代码生成")
        config_path = os.path.join(args.config_dir, "generator_production_oc.json")
        print(f"配置文件：{config_path}")
        
        try:
            config = load_config(config_path)
            vocabulary = load_vocabulary(config["vocabularyFile"])
            stats = generate_code(config, vocabulary)
            all_stats["OC 代码"] = stats
            print_stats("OC 代码", stats)
        except Exception as e:
            print(f"  错误：{e}")
            return 1
    
    # 2. C++ 代码生成
    if run_all or args.cpp:
        print_header("模式 2: C++ 代码生成")
        config_path = os.path.join(args.config_dir, "generator_production_cpp.json")
        print(f"配置文件：{config_path}")
        
        try:
            config = load_config(config_path)
            vocabulary = load_vocabulary(config["vocabularyFile"])
            stats = generate_code(config, vocabulary)
            all_stats["C++ 代码"] = stats
            print_stats("C++ 代码", stats)
        except Exception as e:
            print(f"  错误：{e}")
            return 1
    
    # 3. OC String 常量生成
    if run_all or args.string_oc:
        print_header("模式 3: OC String 常量生成")
        config_path = os.path.join(args.config_dir, "generator_production_string_oc.json")
        print(f"配置文件：{config_path}")
        
        try:
            config = load_config(config_path)
            vocabulary = load_vocabulary(config["vocabularyFile"])
            stats = generate_strings(config, vocabulary)
            all_stats["OC String"] = stats
            print_stats("OC String", stats)
        except Exception as e:
            print(f"  错误：{e}")
            return 1
    
    # 4. C++ String 常量生成
    if run_all or args.string_cpp:
        print_header("模式 4: C++ String 常量生成")
        config_path = os.path.join(args.config_dir, "generator_production_string_cpp.json")
        print(f"配置文件：{config_path}")
        
        try:
            config = load_config(config_path)
            vocabulary = load_vocabulary(config["vocabularyFile"])
            stats = generate_strings(config, vocabulary)
            all_stats["C++ String"] = stats
            print_stats("C++ String", stats)
        except Exception as e:
            print(f"  错误：{e}")
            return 1
    
    # 打印总统计
    total_time = time.time() - total_start_time
    print_header("总统计")
    
    total_files = sum(s.get("files", 0) for s in all_stats.values())
    total_lines = sum(s.get("lines", 0) for s in all_stats.values())
    
    print(f"  总文件数：{total_files:,}")
    print(f"  总行数：{total_lines:,}")
    print(f"  总执行时间：{total_time:.2f} 秒")
    
    print("\n各模式统计:")
    for mode_name, stats in all_stats.items():
        files = stats.get("files", 0)
        lines = stats.get("lines", 0)
        exec_time = stats.get("execution_time", 0)
        print(f"  {mode_name}: {files} 文件，{lines:,} 行，{exec_time:.2f} 秒")
    
    print_header("生成完成")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
