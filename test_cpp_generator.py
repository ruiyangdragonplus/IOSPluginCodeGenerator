#!/usr/bin/env python3
"""
C++ 生成器测试脚本
验证完全独立的 C++ 代码生成器是否正常工作
"""

import sys
import os

# 添加核心模块路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.cpp_generator import CppGenerator
from core.cpp_templates import CppTemplateEngine, CPP_METHOD_TEMPLATES
from core.cpp_types import CppTypeSystem


def test_cpp_template_engine():
    """测试 C++ 模板引擎"""
    print("=" * 60)
    print("测试 C++ 模板引擎")
    print("=" * 60)
    
    engine = CppTemplateEngine()
    
    # 测试模板选择
    for class_type in ["manager", "service", "factory", "storage", "processor"]:
        template = engine.select_template(class_type, "high")
        print(f"\n类类型：{class_type}")
        print(f"  选中模板：{template.get('description', 'N/A')}")
        print(f"  签名格式：{template.get('signature_format', 'N/A')}")
        print(f"  复杂度：{template.get('complexity', 'N/A')}")
    
    print("\n[PASS] C++ 模板引擎测试通过")
    return True


def test_cpp_type_system():
    """测试 C++ 类型系统"""
    print("\n" + "=" * 60)
    print("测试 C++ 类型系统")
    print("=" * 60)
    
    type_system = CppTypeSystem()
    
    # 测试类型获取
    print("\n类型获取测试:")
    print(f"  string 类型：{type_system.get_type('string')}")
    print(f"  number 类型：{type_system.get_type('number')}")
    print(f"  boolean 类型：{type_system.get_type('boolean')}")
    print(f"  container 类型：{type_system.get_type('container')}")
    
    # 测试默认值
    print("\n默认值测试:")
    test_types = ["void", "int", "bool", "std::string", "void*", "std::vector<void*>"]
    for t in test_types:
        default = type_system.get_default_value(t)
        print(f"  {t} -> {default}")
    
    # 测试类型判断
    print("\n类型判断测试:")
    print(f"  int 是基本类型：{type_system.is_primitive_type('int')}")
    print(f"  std::string 是容器类型：{type_system.is_container_type('std::string')}")
    print(f"  std::vector<void*> 是容器类型：{type_system.is_container_type('std::vector<void*>')}")
    print(f"  void* 是指针类型：{type_system.is_pointer_type('void*')}")
    
    print("\n[PASS] C++ 类型系统测试通过")
    return True


def test_cpp_generator_header():
    """测试 C++ 头文件生成"""
    print("\n" + "=" * 60)
    print("测试 C++ 头文件生成")
    print("=" * 60)
    
    generator = CppGenerator()
    generator.set_seed(12345)
    
    # 测试类名
    class_name = "ABDataCacheManager"
    
    # 生成成员变量
    members = [
        {"name": "cacheSize_", "type": "int"},
        {"name": "maxCacheSize_", "type": "size_t"},
        {"name": "enabled_", "type": "bool"}
    ]
    
    # 生成方法
    methods = []
    for i in range(3):
        method_info = generator.generate_method_with_template(class_name, i)
        methods.append(method_info)
    
    # 生成头文件
    header = generator.generate_header(class_name, members=members, methods=methods)
    
    print("\n生成的头文件:")
    print("-" * 40)
    print(header)
    print("-" * 40)
    
    # 验证头文件内容
    assert "#pragma once" in header, "缺少 #pragma once"
    assert "#include <string>" in header, "缺少 #include <string>"
    assert "#include <vector>" in header, "缺少 #include <vector>"
    assert "#include <map>" in header, "缺少 #include <map>"
    assert "#include <functional>" in header, "缺少 #include <functional>"
    assert f"class {class_name}" in header, f"缺少类声明 {class_name}"
    assert "sharedInstance()" in header, "缺少单例方法"
    assert "cache_" in header, "缺少 cache_ 成员"
    
    print("\n[PASS] C++ 头文件生成测试通过")
    return True


def test_cpp_generator_implementation():
    """测试 C++ 实现文件生成"""
    print("\n" + "=" * 60)
    print("测试 C++ 实现文件生成")
    print("=" * 60)
    
    generator = CppGenerator()
    generator.set_seed(12345)
    
    class_name = "ABDataCacheManager"
    
    members = [
        {"name": "cacheSize_", "type": "int"},
        {"name": "maxCacheSize_", "type": "size_t"}
    ]
    
    methods = []
    for i in range(3):
        method_info = generator.generate_method_with_template(class_name, i)
        methods.append(method_info)
    
    # 生成实现文件
    impl = generator.generate_implementation(class_name, members=members, methods=methods)
    
    print("\n生成的实现文件:")
    print("-" * 40)
    print(impl)
    print("-" * 40)
    
    # 验证实现文件内容
    assert f'#include "{class_name}.hpp"' in impl, "缺少头文件包含"
    assert f"{class_name}::{class_name}()" in impl, "缺少构造函数"
    assert f"{class_name}::~{class_name}()" in impl, "缺少析构函数"
    assert "sharedInstance()" in impl, "缺少单例实现"
    assert "std::cout" in impl, "缺少 C++ 输出语句"
    
    # 验证没有 Objective-C 语法
    assert "NSLog" not in impl, "包含 Objective-C 语法 NSLog"
    assert "@\"" not in impl, "包含 Objective-C 字符串语法"
    assert "dispatch_async" not in impl, "包含 Objective-C GCD 语法"
    assert "instancetype" not in impl, "包含 Objective-C instancetype"
    assert "[self " not in impl, "包含 Objective-C 消息发送语法"
    assert "@end" not in impl, "包含 Objective-C @end"
    assert "@interface" not in impl, "包含 Objective-C @interface"
    assert "@implementation" not in impl, "包含 Objective-C @implementation"
    
    print("\n[PASS] C++ 实现文件生成测试通过（无 Objective-C 语法）")
    return True


def test_cpp_generator_complete():
    """测试完整的 C++ 类生成"""
    print("\n" + "=" * 60)
    print("测试完整的 C++ 类生成")
    print("=" * 60)
    
    generator = CppGenerator()
    generator.set_seed(42)
    
    class_name = "ABNetworkService"
    
    # 生成完整的类文件
    files = generator.generate_class(class_name, method_count=5)
    
    print(f"\n生成 {len(files)} 个文件:")
    for file_info in files:
        print(f"\n文件：{file_info['filename']}")
        print("-" * 40)
        print(file_info['content'][:1500])  # 只显示前 1500 字符
        print("..." if len(file_info['content']) > 1500 else "")
        print("-" * 40)
    
    # 验证文件内容
    header_content = files[0]['content']
    impl_content = files[1]['content']
    
    # 头文件验证
    assert files[0]['filename'] == f"{class_name}.hpp", "头文件名错误"
    assert "#pragma once" in header_content, "缺少 #pragma once"
    assert f"class {class_name}" in header_content, "缺少类声明"
    
    # 实现文件验证
    assert files[1]['filename'] == f"{class_name}.cpp", "实现文件名错误"
    assert f'#include "{class_name}.hpp"' in impl_content, "缺少头文件包含"
    
    # 验证纯 C++ 语法
    objc_patterns = ["NSLog", "@\"", "dispatch_async", "instancetype", "@end", "@interface", "@implementation", "[self "]
    for pattern in objc_patterns:
        assert pattern not in impl_content, f"包含 Objective-C 语法：{pattern}"
    
    print("\n[PASS] 完整的 C++ 类生成测试通过")
    return True


def test_all_templates():
    """测试所有 C++ 模板"""
    print("\n" + "=" * 60)
    print("测试所有 C++ 模板")
    print("=" * 60)
    
    generator = CppGenerator()
    
    print(f"\n共有 {len(CPP_METHOD_TEMPLATES)} 个 C++ 模板:")
    
    for template_name, template in CPP_METHOD_TEMPLATES.items():
        print(f"\n模板：{template_name}")
        print(f"  描述：{template.get('description', 'N/A')}")
        print(f"  签名：{template.get('signature_format', 'N/A')}")
        print(f"  适用类型：{template.get('applicable_types', [])}")
        print(f"  复杂度：{template.get('complexity', 'N/A')}")
        
        # 生成示例方法体
        body = generator.cpp_template_engine.generate_body(template, "void", "TestClass", False)
        print(f"  方法体示例:")
        for line in body[:3]:
            print(f"    {line}")
    
    print("\n[PASS] 所有 C++ 模板测试通过")
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("C++ 生成器完全独立测试")
    print("=" * 60)
    
    all_passed = True
    
    try:
        all_passed &= test_cpp_template_engine()
        all_passed &= test_cpp_type_system()
        all_passed &= test_cpp_generator_header()
        all_passed &= test_cpp_generator_implementation()
        all_passed &= test_cpp_generator_complete()
        all_passed &= test_all_templates()
    except Exception as e:
        print(f"\n[FAIL] 测试失败：{e}")
        import traceback
        traceback.print_exc()
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("所有测试通过！[PASS]")
        print("C++ 生成器已完全独立于 Objective-C")
    else:
        print("部分测试失败！[FAIL]")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
