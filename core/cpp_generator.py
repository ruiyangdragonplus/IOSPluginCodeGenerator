"""
C++ 代码生成器模块
负责生成 .h 头文件和 .cpp 实现文件
"""

from typing import Dict, List, Any, Optional


class CppGenerator:
    """C++ 代码生成器类"""
    
    def __init__(self, class_prefix: str = ""):
        """
        初始化 C++ 生成器
        
        Args:
            class_prefix: 类名前缀
        """
        self.class_prefix = class_prefix
    
    def generate_header(
        self,
        class_name: str,
        members: Optional[List[Dict[str, str]]] = None,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        生成 C++ 头文件内容
        
        Args:
            class_name: 类名
            members: 成员变量列表，每个元素包含 name 和 type
            methods: 方法列表，每个元素包含 name, return_type, params, is_const
            
        Returns:
            头文件内容
        """
        lines = []
        
        # 头部保护
        lines.append("#pragma once")
        lines.append("")
        
        # 包含头文件
        lines.append("#include <string>")
        lines.append("#include <vector>")
        lines.append("")
        
        # 类声明
        lines.append(f"class {class_name} {{")
        lines.append("public:")
        
        # 构造函数
        lines.append(f"    {class_name}();")
        lines.append(f"    ~{class_name}();")
        lines.append("")
        
        # 方法声明
        if methods:
            lines.append("    // Methods")
            for method in methods:
                method_decl = self._generate_method_declaration(method)
                lines.append(method_decl)
            lines.append("")
        
        # 成员变量
        if members:
            lines.append("private:")
            for member in members:
                member_name = member.get("name", "")
                member_type = member.get("type", "int")
                lines.append(f"    {member_type} {member_name};")
            lines.append("")
        
        lines.append("};")
        
        return "\n".join(lines)
    
    def _generate_method_declaration(self, method: Dict[str, Any]) -> str:
        """
        生成方法声明
        
        Args:
            method: 方法信息
            
        Returns:
            方法声明字符串
        """
        method_name = method.get("name", "")
        return_type = method.get("return_type", "void")
        params = method.get("params", [])
        is_const = method.get("is_const", False)
        
        # 构建参数列表
        param_strs = []
        for param in params:
            param_name = param.get("name", "")
            param_type = param.get("type", "int")
            param_strs.append(f"{param_type} {param_name}")
        
        params_str = ", ".join(param_strs)
        
        # 构建完整声明
        decl = f"    {return_type} {method_name}({params_str})"
        if is_const:
            decl += " const"
        decl += ";"
        
        return decl
    
    def generate_implementation(
        self,
        class_name: str,
        members: Optional[List[Dict[str, str]]] = None,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        生成 C++ 实现文件内容
        
        Args:
            class_name: 类名
            members: 成员变量列表
            methods: 方法列表
            
        Returns:
            实现文件内容
        """
        lines = []
        
        # 包含头文件
        lines.append(f'#include "{class_name}.hpp"')
        lines.append('#include <iostream>')
        lines.append("")
        
        # 构造函数实现
        lines.append(f"{class_name}::{class_name}() {{")
        if members:
            for member in members:
                member_name = member.get("name", "")
                member_type = member.get("type", "int")
                default_value = self._get_default_value(member_type)
                lines.append(f"    {member_name} = {default_value};")
        lines.append("}")
        lines.append("")
        
        # 析构函数实现
        lines.append(f"{class_name}::~{class_name}() {{")
        lines.append("    // Destructor")
        lines.append("}")
        lines.append("")
        
        # 方法实现
        if methods:
            for method in methods:
                method_impl = self._generate_method_implementation(class_name, method)
                lines.append(method_impl)
                lines.append("")
        
        return "\n".join(lines)
    
    def _get_default_value(self, member_type: str) -> str:
        """
        获取类型的默认值
        
        Args:
            member_type: 类型名
            
        Returns:
            默认值字符串
        """
        if member_type in ["int", "long", "short", "size_t"]:
            return "0"
        elif member_type in ["float", "double"]:
            return "0.0f"
        elif member_type == "bool":
            return "false"
        elif member_type == "std::string":
            return '""'
        elif member_type.startswith("std::vector"):
            return "{}"
        else:
            return "0"
    
    def _generate_method_implementation(self, class_name: str, method: Dict[str, Any]) -> str:
        """
        生成方法实现
        
        Args:
            class_name: 类名
            method: 方法信息
            
        Returns:
            方法实现字符串
        """
        method_name = method.get("name", "")
        return_type = method.get("return_type", "void")
        params = method.get("params", [])
        complexity = method.get("complexity", 1)
        is_const = method.get("is_const", False)
        
        # 构建方法签名
        param_strs = []
        for param in params:
            param_name = param.get("name", "")
            param_type = param.get("type", "int")
            param_strs.append(f"{param_type} {param_name}")
        
        params_str = ", ".join(param_strs)
        
        # 方法签名
        sig = f"{class_name}::{return_type} {method_name}({params_str})"
        if is_const:
            sig += " const"
        
        lines = []
        lines.append(f"{sig} {{")
        
        # 生成方法体
        body_lines = self._generate_method_body(complexity, params, return_type)
        for body_line in body_lines:
            lines.append(f"    {body_line}")
        
        # 返回值
        if return_type != "void":
            if return_type in ["int", "long", "short", "size_t"]:
                lines.append("    return 0;")
            elif return_type in ["float", "double"]:
                lines.append("    return 0.0f;")
            elif return_type == "bool":
                lines.append("    return false;")
            elif return_type == "std::string":
                lines.append('    return "";')
            elif return_type.startswith("std::vector"):
                lines.append("    return {};")
            else:
                lines.append("    return {};")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_method_body(self, complexity: int, params: List[Dict], return_type: str) -> List[str]:
        """
        根据复杂度生成方法体内容
        
        Args:
            complexity: 复杂度等级
            params: 参数列表
            return_type: 返回类型
            
        Returns:
            方法体行列表
        """
        lines = []
        
        if complexity == 1:
            # 简单方法
            lines.append("// Simple implementation")
            lines.append('std::cout << __FUNCTION__ << " called" << std::endl;')
        
        elif complexity == 2:
            # 中等方法
            lines.append("// Medium complexity implementation")
            lines.append('std::cout << __FUNCTION__ << " called" << std::endl;')
            lines.append("")
            lines.append("if (true) {")
            lines.append("    // Process request")
            lines.append("}")
        
        elif complexity >= 3:
            # 复杂方法
            lines.append("// Complex implementation")
            lines.append('std::cout << __FUNCTION__ << " called" << std::endl;')
            lines.append("")
            lines.append("for (int i = 0; i < 10; i++) {")
            lines.append("    // Process item")
            lines.append("    if (i % 2 == 0) {")
            lines.append('        std::cout << "Processing even index: " << i << std::endl;')
            lines.append("    }")
            lines.append("}")
        
        return lines
    
    def generate_files(
        self,
        class_name: str,
        members: Optional[List[Dict[str, str]]] = None,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, str]]:
        """
        生成完整的类文件（头文件和实现文件）
        
        Args:
            class_name: 类名
            members: 成员变量列表
            methods: 方法列表
            
        Returns:
            文件列表，包含 filename 和 content
        """
        header_content = self.generate_header(class_name, members=members, methods=methods)
        impl_content = self.generate_implementation(class_name, members=members, methods=methods)
        
        return [
            {"filename": f"{class_name}.hpp", "content": header_content},
            {"filename": f"{class_name}.cpp", "content": impl_content}
        ]
