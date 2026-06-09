"""
代码生成编排器（唯一编排入口）

main.py 与 run_production.py 都调用这里的 generate_code / generate_strings，
避免两套分叉、行为不一致的生成循环。
"""

import json
import os
import time
from typing import Dict, Any, Optional

from .config_loader import ConfigLoader
from .state_store import StateStore
from .name_builder import NameBuilder
from .line_budget import LineBudget
from .file_writer import FileWriter
from .objc_generator import ObjCGenerator
from .cpp_generator import CppGenerator
from .string_generator import StringGenerator
from .registry_generator import RegistryGenerator


def choose_property_type(name_builder: NameBuilder, language: str = "objc") -> str:
    """随机选择属性类型。"""
    if language == "cpp":
        types = ["std::string", "int", "bool", "std::vector<void*>",
                 "std::map<std::string, void*>", "int", "float", "double"]
    else:
        types = ["NSString *", "NSInteger", "BOOL", "NSArray *",
                 "NSDictionary *", "int", "float", "double"]
    return name_builder.random.choice(types)


def choose_return_type(name_builder: NameBuilder,
                       vocabulary: Optional[Dict[str, Any]] = None,
                       language: str = "objc") -> str:
    """随机选择返回类型。"""
    if language == "cpp":
        types = ["void", "void", "void", "int", "bool", "std::string", "int", "float"]
        return name_builder.random.choice(types)
    if vocabulary:
        builtin = vocabulary.get("builtin", {})
        return_types = builtin.get("returnType", {})
        category = name_builder.random.choice(
            ["primitive", "object", "optional", "errorHandling"])
        if category in return_types and return_types[category]:
            return name_builder.random.choice(return_types[category])
    types = ["void", "void", "void", "NSInteger", "BOOL", "NSString *", "int", "float"]
    return name_builder.random.choice(types)


def choose_param_type(name_builder: NameBuilder,
                      vocabulary: Optional[Dict[str, Any]] = None,
                      language: str = "objc") -> str:
    """随机选择参数类型。"""
    if language == "cpp":
        types = ["int", "std::string", "bool", "int", "float", "void*"]
        return name_builder.random.choice(types)
    if vocabulary:
        builtin = vocabulary.get("builtin", {})
        param_types = builtin.get("paramType", {})
        category = name_builder.random.choice(["primitive", "object", "pointer"])
        if category in param_types and param_types[category]:
            return name_builder.random.choice(param_types[category])
    types = ["NSInteger", "NSString *", "BOOL", "int", "float", "id"]
    return name_builder.random.choice(types)


def _build_diversity_config(config: Dict[str, Any]) -> Dict[str, Any]:
    keys = [
        "enableAsyncMethods", "enableBlockCallbacks", "enableErrorHandling",
        "enableGenericTypes", "enableChainableMethods", "enableFactoryMethods",
        "enableSingletonPattern", "enableDelegatePattern", "enableCacheLogic",
        "enableValidationLogic", "enableLoggingLogic",
    ]
    cfg = {k: config.get(k, True) for k in keys}
    cfg["diversityLevel"] = config.get("diversityLevel", "high")
    return cfg


def generate_code(config: Dict[str, Any], vocabulary: Dict[str, Any],
                  progress: bool = False) -> Dict[str, Any]:
    """
    生成 OC / C++ 整类代码。返回统计信息。

    这是唯一的整类生成实现：方法装配（命名 + 类型 + 模板）一处完成，
    头文件声明与实现签名由生成器内的唯一签名渲染器产出，保证一致。
    """
    stats = {"files": 0, "lines": 0, "classes": 0, "execution_time": 0}
    start_time = time.time()

    state_store = StateStore(config["stateFile"])
    state_store.load()

    name_builder = NameBuilder(
        vocabulary=vocabulary.get("custom", vocabulary),
        state_store=state_store,
        class_prefix=config.get("classPrefix", ""),
    )
    name_builder.set_seed(config.get("randomSeed", 12345))

    line_budget = LineBudget(
        total_line_range=tuple(config["totalLineRange"]),
        lines_per_class_range=tuple(config["linesPerClassRange"]),
        methods_per_class_range=tuple(config["methodsPerClassRange"]),
        properties_per_class_range=tuple(config["propertiesPerClassRange"]),
        class_count=config["classCount"],
    )
    line_budget.set_seed(config.get("randomSeed", 12345))
    budgets = line_budget.allocate_budgets()

    file_writer = FileWriter(
        output_dir=config["outputDir"],
        overwrite=config.get("overwrite", False),
    )
    file_writer.ensure_output_dir()

    diversity_config = _build_diversity_config(config)
    language = config["language"]
    if language == "objc":
        generator = ObjCGenerator(class_prefix=config.get("classPrefix", ""),
                                  vocabulary=vocabulary, diversity_config=diversity_config)
    else:
        generator = CppGenerator(class_prefix=config.get("classPrefix", ""),
                                 vocabulary=vocabulary, diversity_config=diversity_config)
    generator.set_seed(config.get("randomSeed", 12345))

    total_lines = 0
    generated_classes = []
    high_diversity = diversity_config.get("diversityLevel", "high") == "high"

    for i, budget in enumerate(budgets):
        class_name = name_builder.generate_class_name()
        if not class_name:
            print(f"  警告：无法生成唯一类名，跳过第 {i + 1} 个类")
            continue

        properties = []
        prop_names = name_builder.generate_property_names(budget["properties_count"])
        for prop_name in prop_names:
            properties.append({"name": prop_name,
                               "type": choose_property_type(name_builder, language)})

        methods = []
        method_names = name_builder.generate_method_names(budget["methods_count"])
        used_method_names = set()

        for idx in range(budget["methods_count"]):
            if high_diversity:
                method_info = generator.generate_method_with_template(class_name, idx)
                template = method_info.get("template", {})
                signature_format = template.get("signature_format", "")

                if "sharedInstance" in signature_format or "createInstance" in signature_format:
                    method_name = method_info["name"]
                    if method_name in used_method_names:
                        method_name = method_names[idx] if idx < len(method_names) else f"method{idx}"
                        base_name, counter = method_name, 0
                        while method_name in used_method_names:
                            counter += 1
                            method_name = f"{base_name}{counter}"
                        used_method_names.add(method_name)
                        method_info["name"] = method_name
                    else:
                        used_method_names.add(method_name)
                else:
                    method_name = method_names[idx] if idx < len(method_names) else f"method{idx}"
                    base_name, counter = method_name, 0
                    while method_name in used_method_names:
                        counter += 1
                        method_name = f"{base_name}{counter}"
                    used_method_names.add(method_name)
                    method_info["name"] = method_name

                # 模板未定义参数时才补随机参数
                if not method_info.get("params", []):
                    if name_builder.random.random() > 0.5:
                        params = []
                        for j in range(name_builder.random.randint(1, 2)):
                            params.append({"name": f"param{j}",
                                          "type": choose_param_type(name_builder, vocabulary, language)})
                        method_info["params"] = params

                # 返回类型：模板已解析出具体类型（含 ClassName& 链式）则尊重之；
                # 仅当为空或 void 时再补（OC 可从签名提取，C++ 走随机）
                if not method_info.get("return_type") or method_info["return_type"] == "void":
                    import re
                    rt_match = re.search(r'[\+\-]\s*\(([^)]+)\)', signature_format)
                    if rt_match:
                        extracted = rt_match.group(1).strip()
                        method_info["return_type"] = extracted if extracted != "void" \
                            else choose_return_type(name_builder, vocabulary, language)
                    else:
                        method_info["return_type"] = choose_return_type(name_builder, vocabulary, language)
                methods.append(method_info)
            else:
                method_name = method_names[idx] if idx < len(method_names) else f"method{idx}"
                base_name, counter = method_name, 0
                while method_name in used_method_names:
                    counter += 1
                    method_name = f"{base_name}{counter}"
                used_method_names.add(method_name)
                params = []
                if name_builder.random.random() > 0.5:
                    for j in range(name_builder.random.randint(1, 2)):
                        params.append({"name": f"param{j}",
                                      "type": choose_param_type(name_builder, vocabulary, language)})
                methods.append({
                    "name": method_name,
                    "return_type": choose_return_type(name_builder, vocabulary, language),
                    "params": params,
                    "complexity": line_budget.get_method_complexity(budget["lines_per_method"]),
                })

        if language == "objc":
            files = generator.generate_files(class_name=class_name,
                                             properties=properties, methods=methods)
        else:
            members = [{"name": p["name"], "type": p["type"]} for p in properties]
            files = generator.generate_files(class_name=class_name,
                                             members=members, methods=methods)

        file_writer.write_files(files)
        for file_info in files:
            file_path = os.path.join(file_writer.output_dir, file_info["filename"])
            state_store.mark_file_generated(file_path)
            total_lines += len(file_info["content"].split("\n"))

        generated_classes.append(class_name)
        stats["files"] += len(files)
        stats["classes"] += 1

        if progress and (i + 1) % 100 == 0:
            print(f"  进度：{i + 1}/{config['classCount']} 类，已生成 {total_lines} 行")

    if config.get("generateRegistry", False):
        registry_language = config.get("registryLanguage", language)
        all_classes = state_store.get_used_class_names()
        registry_generator = RegistryGenerator(class_prefix=config.get("classPrefix", "MX11"))
        registry_file = registry_generator.generate_registry(all_classes, registry_language)
        file_writer.write_file(registry_file["filename"], registry_file["content"], check_exists=False)
        header_file = registry_generator.generate_header_file(all_classes, registry_language)
        file_writer.write_file(header_file["filename"], header_file["content"], check_exists=False)
        for fpath in (registry_file["filename"], header_file["filename"]):
            state_store.mark_file_generated(os.path.join(file_writer.output_dir, fpath))
        stats["files"] += 2

    state_store.add_history_entry({
        "language": language,
        "generated_classes": generated_classes,
        "total_lines": total_lines,
        "files_written": len(file_writer.get_written_files()),
        "files_skipped": len(file_writer.get_skipped_files()),
    })
    state_store.save()

    stats["lines"] = total_lines
    stats["execution_time"] = time.time() - start_time
    return stats


def generate_strings(config: Dict[str, Any], vocabulary: Dict[str, Any]) -> Dict[str, Any]:
    """生成 String 常量文件。返回统计信息。"""
    stats = {"files": 0, "lines": 0, "strings": 0, "execution_time": 0}
    start_time = time.time()

    state_store = StateStore(config["stateFile"])
    state_store.load()

    string_generator = StringGenerator(vocabulary=vocabulary.get("custom", vocabulary))
    string_generator.set_seed(config.get("randomSeed", 12345))

    string_count = config.get("stringCount", 5000)
    string_mode = config.get("stringMode", "word")
    string_language = config.get("stringLanguage", "objc")
    output_filename = config.get("outputFileName", "MX11StringConstants")

    file_writer = FileWriter(output_dir=config["outputDir"],
                             overwrite=config.get("overwrite", False))
    file_writer.ensure_output_dir()

    file_info = string_generator.generate_file(
        string_count=string_count, language=string_language,
        mode=string_mode, prefix=config.get("classPrefix", "MX11"),
        output_filename=output_filename,
    )

    result = file_writer.write_files([file_info])
    state_store.mark_file_generated(
        os.path.join(file_writer.output_dir, file_info["filename"]))
    state_store.save()

    stats["files"] = result["written"]
    stats["lines"] = len(file_info["content"].split("\n"))
    stats["strings"] = string_count
    stats["execution_time"] = time.time() - start_time

    stats_file_path = os.path.join(config["outputDir"], "generation_stats.json")
    with open(stats_file_path, "w", encoding="utf-8") as f:
        json.dump({
            "string_count": string_count, "file_lines": stats["lines"],
            "execution_time": stats["execution_time"],
            "output_file": file_info["filename"], "mode": string_mode,
            "language": string_language,
        }, f, indent=2)
    return stats
