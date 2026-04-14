"""
统一入口注册表生成器模块
负责生成 ABPluginRegistry.m (Objective-C) 和 ABPluginRegistry.cpp (C++) 文件
"""

import os
from typing import Dict, List, Any, Optional


class RegistryGenerator:
    """统一入口注册表生成器"""
    
    def __init__(self, class_prefix: str = "AB"):
        """
        初始化注册表生成器
        
        Args:
            class_prefix: 类名前缀
        """
        self.class_prefix = class_prefix
    
    def generate_objc_registry(self, generated_classes: List[str]) -> str:
        """
        生成 Objective-C 统一入口文件
        
        Args:
            generated_classes: 已生成的类名列表
            
        Returns:
            ABPluginRegistry.m 文件内容
        """
        lines = []
        
        # 文件头注释
        lines.append("//")
        lines.append("// ABPluginRegistry.m")
        lines.append("// 自动生成的插件注册表 - 统一入口")
        lines.append("// 警告：此文件由工具自动生成，请勿手动修改")
        lines.append("//")
        lines.append("")
        lines.append("#import <Foundation/Foundation.h>")
        lines.append("")
        
        # 导入所有生成的类
        lines.append("// 导入所有生成的类")
        for class_name in generated_classes:
            lines.append(f'#import "{class_name}.h"')
        lines.append("")
        
        # 静态变量用于防止重复初始化
        lines.append("// 初始化状态标记")
        lines.append("static BOOL ABPluginsInitialized = NO;")
        lines.append("")
        
        # 统一初始化入口
        lines.append("// 统一初始化入口")
        lines.append("void ABInitializeAllPlugins() {")
        lines.append("    if (ABPluginsInitialized) return;")
        lines.append("    ABPluginsInitialized = YES;")
        lines.append("")
        lines.append("    NSLog(@\"[ABPlugin] Initializing all plugins...\");")
        lines.append("")
        
        # 自动实例化并调用所有生成的类
        lines.append("    // 自动实例化并调用所有生成的类")
        for i, class_name in enumerate(generated_classes, 1):
            var_name = f"m{i}"
            lines.append(f"    {class_name} *{var_name} = [[{class_name} alloc] init];")
            # 尝试调用 loadData 方法（如果存在）
            lines.append(f"    [{var_name} loadData];")
            lines.append("")
        
        lines.append("    NSLog(@\"[ABPlugin] All plugins initialized successfully.\");")
        lines.append("}")
        lines.append("")
        
        # 统一清理入口
        lines.append("// 统一清理入口")
        lines.append("void ABCleanupAllPlugins() {")
        lines.append("    if (!ABPluginsInitialized) return;")
        lines.append("")
        lines.append("    NSLog(@\"[ABPlugin] Cleaning up all plugins...\");")
        lines.append("")
        lines.append("    // 清理逻辑")
        lines.append("    // 注意：Objective-C 使用 ARC 自动内存管理，无需手动释放")
        lines.append("")
        lines.append("    ABPluginsInitialized = NO;")
        lines.append("    NSLog(@\"[ABPlugin] All plugins cleaned up successfully.\");")
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_cpp_registry(self, generated_classes: List[str]) -> str:
        """
        生成 C++ 统一入口文件
        
        Args:
            generated_classes: 已生成的类名列表
            
        Returns:
            ABPluginRegistry.cpp 文件内容
        """
        lines = []
        
        # 文件头注释
        lines.append("//")
        lines.append("// ABPluginRegistry.cpp")
        lines.append("// 自动生成的插件注册表 - 统一入口")
        lines.append("// 警告：此文件由工具自动生成，请勿手动修改")
        lines.append("//")
        lines.append("")
        
        # 导入所有生成的类（使用 .h 扩展名以便 Unity 识别）
        lines.append("// 导入所有生成的类")
        for class_name in generated_classes:
            lines.append(f'#include "{class_name}.h"')
        lines.append("")
        
        # 包含必要的头文件
        lines.append("#include <iostream>")
        lines.append("")
        
        # 静态变量用于防止重复初始化
        lines.append("// 初始化状态标记")
        lines.append("static bool g_ABPluginsInitialized = false;")
        lines.append("")
        
        # extern "C" 包装，便于 C# P/Invoke 调用
        lines.append('extern "C" {')
        lines.append("")
        
        # 统一初始化入口
        lines.append("    // 统一初始化入口")
        lines.append("    void ABInitializeAllPlugins() {")
        lines.append("        if (g_ABPluginsInitialized) return;")
        lines.append("        g_ABPluginsInitialized = true;")
        lines.append("")
        lines.append('        std::cout << "[ABPlugin] Initializing all plugins..." << std::endl;')
        lines.append("")
        
        # 实例化并调用所有生成的类
        lines.append("        // 实例化并调用所有生成的类")
        for i, class_name in enumerate(generated_classes, 1):
            var_name = f"m{i}"
            lines.append(f"        {class_name}* {var_name} = new {class_name}();")
            # 尝试调用 loadData 方法（如果存在）
            lines.append(f"        {var_name}->loadData();")
            # 注意：实际使用中需要考虑内存管理，这里简单示例
            lines.append(f"        delete {var_name};")
            lines.append("")
        
        lines.append('        std::cout << "[ABPlugin] All plugins initialized successfully." << std::endl;')
        lines.append("    }")
        lines.append("")
        
        # 统一清理入口
        lines.append("    // 统一清理入口")
        lines.append("    void ABCleanupAllPlugins() {")
        lines.append("        if (!g_ABPluginsInitialized) return;")
        lines.append("")
        lines.append('        std::cout << "[ABPlugin] Cleaning up all plugins..." << std::endl;')
        lines.append("")
        lines.append("        // 清理逻辑")
        lines.append("        // 注意：C++ 需要手动管理内存")
        lines.append("")
        lines.append("        g_ABPluginsInitialized = false;")
        lines.append('        std::cout << "[ABPlugin] All plugins cleaned up successfully." << std::endl;')
        lines.append("    }")
        lines.append("")
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_registry(self, generated_classes: List[str], language: str = "objc") -> Dict[str, str]:
        """
        根据语言生成注册表文件
        
        Args:
            generated_classes: 已生成的类名列表
            language: 目标语言 (objc 或 cpp)
            
        Returns:
            文件信息字典，包含 filename 和 content
        """
        if language == "objc":
            content = self.generate_objc_registry(generated_classes)
            return {"filename": "ABPluginRegistry.m", "content": content}
        elif language == "cpp":
            content = self.generate_cpp_registry(generated_classes)
            return {"filename": "ABPluginRegistry.cpp", "content": content}
        else:
            raise ValueError(f"不支持的语言：{language}。支持的语言：objc, cpp")
    
    def generate_header_file(self, generated_classes: List[str], language: str = "objc") -> Dict[str, str]:
        """
        生成头文件（用于声明初始化函数）
        
        Args:
            generated_classes: 已生成的类名列表
            language: 目标语言 (objc 或 cpp)
            
        Returns:
            文件信息字典，包含 filename 和 content
        """
        lines = []
        
        # 文件头注释
        lines.append("//")
        lines.append("// ABPluginRegistry.h")
        lines.append("// 插件注册表头文件 - 声明统一入口函数")
        lines.append("// 警告：此文件由工具自动生成，请勿手动修改")
        lines.append("//")
        lines.append("")
        
        if language == "cpp":
            # C++ 版本：使用 #include 和 C 链接
            lines.append("#pragma once")
            lines.append("")
            lines.append("#ifdef __cplusplus")
            lines.append('extern "C" {')
            lines.append("#endif")
            lines.append("")
            lines.append("// 统一初始化入口")
            lines.append("void ABInitializeAllPlugins();")
            lines.append("")
            lines.append("// 统一清理入口")
            lines.append("void ABCleanupAllPlugins();")
            lines.append("")
            lines.append("#ifdef __cplusplus")
            lines.append("}")
            lines.append("#endif")
        else:
            # Objective-C 版本
            lines.append("#import <Foundation/Foundation.h>")
            lines.append("")
            lines.append("#ifdef __cplusplus")
            lines.append('extern "C" {')
            lines.append("#endif")
            lines.append("")
            lines.append("// 统一初始化入口")
            lines.append("void ABInitializeAllPlugins();")
            lines.append("")
            lines.append("// 统一清理入口")
            lines.append("void ABCleanupAllPlugins();")
            lines.append("")
            lines.append("#ifdef __cplusplus")
            lines.append("}")
            lines.append("#endif")
        
        content = "\n".join(lines)
        return {"filename": "ABPluginRegistry.h", "content": content}
