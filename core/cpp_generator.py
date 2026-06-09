"""
C++ 代码生成器模块
完全独立于 Objective-C 的 C++ 代码生成器
负责生成 .h 头文件和 .cpp 实现文件（使用 .h 以便 Unity iOS 构建系统识别）
"""

from typing import Dict, List, Any, Optional, Tuple
from .cpp_templates import CppTemplateEngine, CPP_METHOD_TEMPLATES, CPP_CODE_BLOCKS
from .cpp_types import CppTypeSystem, CPP_DEFAULT_VALUES


class CppGenerator:
    """C++ 代码生成器类 - 完全独立于 Objective-C"""
    
    # 类类型映射（从词库获取类名后用于选择模板）
    CLASS_TYPE_MAPPING: Dict[str, str] = {
        "Manager": "manager",
        "Controller": "manager",
        "Director": "manager",
        "Supervisor": "manager",
        "Coordinator": "coordinator",
        "Service": "service",
        "Provider": "service",
        "Handler": "service",
        "Processor": "processor",
        "Transformer": "processor",
        "Parser": "processor",
        "Storage": "storage",
        "Repository": "storage",
        "Archive": "storage",
        "Registry": "storage",
        "Factory": "factory",
        "Builder": "factory",
        "Generator": "factory",
        "Creator": "factory",
        "Observer": "observer",
        "Listener": "observer",
        "Watcher": "observer",
        "Monitor": "observer",
        "Adapter": "adapter",
        "Wrapper": "adapter",
        "Proxy": "adapter",
        "Bridge": "adapter",
        "Decorator": "adapter",
    }
    
    def __init__(self, class_prefix: str = "", vocabulary: Optional[Dict[str, Any]] = None,
                 diversity_config: Optional[Dict[str, Any]] = None):
        """
        初始化 C++ 生成器
        
        Args:
            class_prefix: 类名前缀
            vocabulary: 词库配置（仅用于命名，不用于代码模板）
            diversity_config: 多样性配置
        """
        self.class_prefix = class_prefix
        self.vocabulary = vocabulary or {}
        
        # 使用独立的 C++ 模板引擎
        self.cpp_template_engine = CppTemplateEngine()
        
        # 使用独立的 C++ 类型系统
        self.cpp_type_system = CppTypeSystem()
        
        self.diversity_config = diversity_config or {
            "diversityLevel": "high",
            "enableAsyncMethods": True,
            "enableCallbackMethods": True,
            "enableErrorHandling": True,
            "enableGenericTypes": True,
            "enableChainableMethods": True,
            "enableFactoryMethods": True,
            "enableSingletonPattern": True,
            "enableCacheLogic": True,
            "enableValidationLogic": True,
            "enableLoggingLogic": True
        }
    
    def set_seed(self, seed: int):
        """设置随机种子"""
        self.cpp_template_engine.rng.seed(seed)
        self.cpp_type_system.set_seed(seed)
    
    def detect_class_type(self, class_name: str) -> str:
        """
        从类名识别类类型
        
        Args:
            class_name: 类名
            
        Returns:
            类类型字符串
        """
        for suffix, class_type in self.CLASS_TYPE_MAPPING.items():
            if class_name.endswith(suffix):
                return class_type
        return "manager"  # 默认类型
    
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
            methods: 方法列表，每个元素包含 name, return_type, params
            
        Returns:
            头文件内容
        """
        lines = []
        
        # 头部保护
        lines.append("#pragma once")
        lines.append("")
        
        # 收集所有需要的头文件
        required_includes = set()
        required_includes.add("<string>")
        required_includes.add("<vector>")
        required_includes.add("<map>")
        required_includes.add("<functional>")
        required_includes.add("<memory>")
        
        # 根据方法和成员类型添加头文件
        if methods:
            for method in methods:
                return_type = method.get("return_type", "void")
                params = method.get("params", [])
                
                # 检查返回类型
                for type_name, include in self.cpp_type_system.type_includes.items():
                    if return_type.startswith(type_name):
                        required_includes.add(include)
                
                # 检查参数类型
                for param in params:
                    param_type = param.get("type", "void")
                    for type_name, include in self.cpp_type_system.type_includes.items():
                        if param_type.startswith(type_name):
                            required_includes.add(include)
        
        # 添加必要的头文件
        lines.append("#include <string>")
        lines.append("#include <vector>")
        lines.append("#include <map>")
        lines.append("#include <functional>")
        lines.append("#include <memory>")
        lines.append("#include <iostream>")
        
        # 检查是否需要 future（异步方法）
        if methods:
            for method in methods:
                template = method.get("template", {})
                if template and "async" in template.get("description", "").lower():
                    lines.append("#include <future>")
                    break
        
        lines.append("")
        
        # 类声明
        lines.append(f"class {class_name} {{")
        lines.append("public:")
        
        # 构造函数
        lines.append(f"    // Constructor")
        lines.append(f"    {class_name}();")
        lines.append(f"    virtual ~{class_name}();")
        lines.append("")
        
        # 成员变量
        if members:
            lines.append("private:")
            for member in members:
                member_name = member.get("name", "")
                member_type = member.get("type", "int")
                lines.append(f"    {member_type} {member_name};")
            lines.append("")
        
        # 添加默认私有成员（只声明一次）
        lines.append("private:")
        lines.append("    // Default members")
        lines.append(f"    std::map<std::string, void*> cache_;")
        lines.append(f"    std::string name_;")
        lines.append(f"    bool initialized_;")
        lines.append(f"    int count_;")
        lines.append(f"    int maxCount_;")
        lines.append(f"    void* ptr_;")
        lines.append(f"    void* obj_;")
        lines.append(f"    int index_;")
        lines.append(f"    int size_;")
        lines.append(f"    void* currentValue_;")
        lines.append("")
        
        # 单例方法（如果类类型支持）- 只声明一次
        class_type = self.detect_class_type(class_name)
        if class_type in ["manager", "service", "storage", "registry"]:
            lines.append("public:")
            lines.append(f"    // Singleton")
            lines.append(f"    static {class_name}& sharedInstance();")
            lines.append("")
        
        # 方法声明
        # 使用集合跟踪已声明的方法，避免重复
        declared_methods = set()
        # 如果类类型支持单例，将单例方法签名加入已声明集合
        if class_type in ["manager", "service", "storage", "registry"]:
            declared_methods.add(f"static {class_name}& sharedInstance();")
        
        if methods:
            lines.append("    // Methods")
            for method in methods:
                method_decl = self._generate_method_declaration(method, class_name)
                # 检查是否已声明（通过方法签名）
                method_sig = method_decl.strip()
                if method_sig not in declared_methods:
                    declared_methods.add(method_sig)
                    lines.append(method_decl)
            lines.append("")
        
        lines.append("};")
        
        return "\n".join(lines)
    
    @staticmethod
    def _method_is_static(method: Dict[str, Any]) -> bool:
        """判断方法是否为 static（工厂/单例）。"""
        if method.get("is_static"):
            return True
        sig = method.get("template", {}).get("signature_format", "")
        return sig.strip().startswith("static")

    def _render_cpp_signature(self, method: Dict[str, Any], class_name: str,
                              for_impl: bool) -> str:
        """
        唯一签名渲染器：头文件声明 与 实现定义 共用此函数，
        都从已解析的 return_type + params 渲染，逐字一致（杜绝头实分叉）。

        Args:
            for_impl: True 生成实现签名 "ret Class::name(params)"，
                      False 生成头文件声明 "    [static ]ret name(params);"
        """
        method_name = method.get("name", "")
        return_type = method.get("return_type", "void")
        params = method.get("params", [])
        is_static = self._method_is_static(method)

        param_strs = [
            self.cpp_type_system.generate_param_declaration(
                p.get("name", ""), p.get("type", "void"))
            for p in params
        ]
        params_str = ", ".join(param_strs)

        if for_impl:
            # C++ 定义不重复 static 关键字，且方法名前加 Class::
            return f"{return_type} {class_name}::{method_name}({params_str})"
        prefix = "static " if is_static else ""
        return f"    {prefix}{return_type} {method_name}({params_str});"

    def _generate_method_declaration(self, method: Dict[str, Any], class_name: str = "") -> str:
        """生成 C++ 方法声明（委托唯一签名渲染器）。"""
        return self._render_cpp_signature(method, class_name, for_impl=False)
    
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
        
        # 包含头文件（使用 .h 扩展名以便 Unity 识别）
        lines.append(f'#include "{class_name}.h"')
        lines.append("")
        
        # 包含额外头文件
        lines.append("#include <iostream>")
        lines.append("#include <future>")
        lines.append("")
        
        # 构造函数实现
        lines.append(f"{class_name}::{class_name}() {{")
        lines.append("    // Constructor implementation")
        lines.append("    initialized_ = false;")
        lines.append("    count_ = 0;")
        lines.append("    maxCount_ = 100;")
        lines.append("    ptr_ = nullptr;")
        lines.append("    obj_ = nullptr;")
        lines.append("    index_ = 0;")
        lines.append("    size_ = 0;")
        lines.append("    currentValue_ = nullptr;")
        if members:
            for member in members:
                member_name = member.get("name", "")
                member_type = member.get("type", "int")
                default_value = self.cpp_type_system.get_default_value(member_type)
                lines.append(f"    {member_name} = {default_value};")
        lines.append("}")
        lines.append("")
        
        # 析构函数实现
        lines.append(f"{class_name}::~{class_name}() {{")
        lines.append("    // Destructor implementation")
        lines.append("}")
        lines.append("")
        
        # 单例实现
        class_type = self.detect_class_type(class_name)
        if class_type in ["manager", "service", "storage", "registry"]:
            lines.append(f"{class_name}& {class_name}::sharedInstance() {{")
            lines.append("    // Thread-safe singleton (C++11)")
            lines.append(f"    static {class_name} instance;")
            lines.append("    return instance;")
            lines.append("}")
            lines.append("")
        
        # 方法实现
        if methods:
            for method in methods:
                method_impl = self._generate_method_implementation(class_name, method)
                lines.append(method_impl)
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_method_implementation(self, class_name: str, method: Dict[str, Any]) -> str:
        """
        生成方法实现（使用 C++ 原生模板）
        
        Args:
            class_name: 类名
            method: 方法信息
            
        Returns:
            方法实现字符串
        """
        return_type = method.get("return_type", "void")
        template = method.get("template", {})

        # 方法签名：与头文件声明共用唯一渲染器，保证逐字一致
        sig = self._render_cpp_signature(method, class_name, for_impl=True)

        lines = []
        lines.append(f"{sig} {{")
        
        # 生成方法体 - 使用 C++ 原生模板
        if template:
            enable_code_blocks = self.diversity_config.get("diversityLevel", "high") == "high"
            body_lines = self.cpp_template_engine.generate_body(
                template, return_type, class_name, enable_code_blocks
            )
        else:
            body_lines = self._generate_cpp_method_body(method.get("complexity", 1), params, return_type)
        
        for body_line in body_lines:
            lines.append(f"    {body_line}")

        # 返回值（如果非 void）：仅当方法体尚未包含 return 时才补兜底，
        # 避免产生不可达的重复 return（止血修复）
        import re as _re
        body_has_return = any(_re.search(r"\breturn\b", bl) for bl in body_lines)
        if return_type != "void" and not body_has_return:
            default_value = self.cpp_type_system.get_default_value(return_type)
            if default_value:
                lines.append(f"    return {default_value};")
            else:
                lines.append("    return {};")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_cpp_method_body(self, complexity: int, params: List[Dict], return_type: str) -> List[str]:
        """
        根据复杂度生成 C++ 方法体内容
        
        Args:
            complexity: 复杂度等级
            params: 参数列表
            return_type: 返回类型
            
        Returns:
            C++ 方法体行列表
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
    
    def generate_method_with_template(self, class_name: str, method_index: int = 0) -> Dict[str, Any]:
        """
        使用模板引擎生成方法（使用 C++ 原生模板）
        
        Args:
            class_name: 类名
            method_index: 方法索引
            
        Returns:
            方法信息字典
        """
        class_type = self.detect_class_type(class_name)
        
        # 使用 C++ 原生模板
        diversity_level = self.diversity_config.get("diversityLevel", "high")
        template = self.cpp_template_engine.select_template(class_type, diversity_level)
        
        # 生成方法名
        method_name = self._generate_method_name_for_template(template, method_index)
        
        # 生成返回类型 - 使用 C++ 类型系统（传入 class_name 以替换占位符）
        return_type = self._get_cpp_return_type_for_template(template, class_name)
        
        # 生成参数
        params = self._generate_cpp_params_for_template(template)
        
        return {
            "name": method_name,
            "return_type": return_type,
            "template": template,
            "class_type": class_type,
            "complexity": template.get("complexity", 1),
            "params": params
        }
    
    def _get_cpp_return_type_for_template(self, template: Dict[str, Any], class_name: str = "") -> str:
        """
        根据模板获取 C++ 返回类型
        
        Args:
            template: 方法模板
            class_name: 类名（用于替换 ClassName 占位符）
            
        Returns:
            C++ 返回类型字符串
        """
        signature_format = template.get("signature_format", "void {method_name}()")
        
        # 处理包含 {return_type} 占位符的情况
        if "{return_type}" in signature_format:
            description = template.get("description", "")
            if "无返回值" in description or "void" in description.lower():
                return "void"
            elif "bool" in description.lower() or "验证" in description:
                return "bool"
            elif "string" in description.lower() or "字符串" in description:
                return "std::string"
            else:
                return "void"
        
        # 链式方法：返回自身引用 ClassName&
        if signature_format.startswith("{class_name}"):
            return class_name + "&"
        # 从签名格式中提取返回类型
        if signature_format.startswith("void "):
            return "void"
        elif signature_format.startswith("bool "):
            return "bool"
        elif signature_format.startswith("std::string "):
            return "std::string"
        elif signature_format.startswith("std::vector<"):
            return "std::vector<void*>"
        elif signature_format.startswith("static "):
            # 处理静态方法 - 替换 ClassName 占位符
            if "std::unique_ptr<" in signature_format:
                # 从签名中提取类名占位符并替换
                return_type = "std::unique_ptr<" + class_name + ">"
                return return_type
            elif "&" in signature_format:
                return class_name + "&"
            return "void"
        elif signature_format.startswith("int "):
            return "int"
        elif signature_format.startswith("void* "):
            return "void*"
        elif signature_format.startswith("std::function<"):
            return "void"
        else:
            # 默认从签名开头提取
            parts = signature_format.split(" ")
            if parts:
                rt = parts[0]
                if rt in ["void", "bool", "int", "float", "double", "size_t", "long", "short"]:
                    return rt
                elif rt.startswith("std::"):
                    return rt
                else:
                    return "void"
            return "void"
    
    def _generate_cpp_params_for_template(self, template: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        根据模板生成 C++ 参数列表
        
        Args:
            template: 方法模板
            
        Returns:
            参数列表
        """
        signature_format = template.get("signature_format", "void {method_name}()")

        # 直接从签名格式解析真实的参数名与类型（而非按类型猜名字），
        # 确保参数名与模板函数体内引用的名字逐字一致，避免未声明标识符。
        start = signature_format.find("(")
        end = signature_format.rfind(")")
        if start == -1 or end == -1 or end <= start + 1:
            return []
        inner = signature_format[start + 1:end].strip()
        if not inner:
            return []

        params = []
        for chunk in self._split_top_level(inner):
            chunk = chunk.strip()
            if not chunk:
                continue
            # 末尾标识符为参数名，其余为类型
            m = __import__("re").match(r"^(.*?)([A-Za-z_]\w*)$", chunk)
            if not m:
                continue
            ptype = m.group(1).strip()
            pname = m.group(2).strip()
            if not ptype:  # 形如 "int"（无名），跳过或按通用名
                ptype, pname = chunk, "param0"
            params.append({"name": pname, "type": ptype})
        return params

    @staticmethod
    def _split_top_level(s: str) -> List[str]:
        """按顶层逗号切分参数（尊重 <> 与 () 的嵌套）。"""
        parts, depth, cur = [], 0, []
        for ch in s:
            if ch in "<(":
                depth += 1
            elif ch in ">)":
                depth -= 1
            if ch == "," and depth == 0:
                parts.append("".join(cur))
                cur = []
            else:
                cur.append(ch)
        if cur:
            parts.append("".join(cur))
        return parts
    
    def _generate_method_name_for_template(self, template: Dict[str, Any], index: int) -> str:
        """
        为模板生成方法名
        
        Args:
            template: 方法模板
            index: 方法索引
            
        Returns:
            方法名
        """
        # 方法名前缀
        prefixes = ["perform", "execute", "handle", "process", "run", "start", "begin", "init"]
        prefix = self.cpp_template_engine.rng.choice(prefixes)
        
        # 方法名主体
        subjects = ["Operation", "Task", "Request", "Command", "Action", "Work", "Job", "Procedure"]
        subject = self.cpp_template_engine.rng.choice(subjects)
        
        return f"{prefix}{subject}{index}"
    
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
            {"filename": f"{class_name}.h", "content": header_content},
            {"filename": f"{class_name}.cpp", "content": impl_content}
        ]
    
    def generate_class(
        self,
        class_name: str,
        method_count: int = 3,
        members: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """
        生成完整的类（自动生成方法）
        
        Args:
            class_name: 类名
            method_count: 方法数量
            members: 成员变量列表（可选）
            
        Returns:
            文件列表
        """
        # 生成方法
        methods = []
        for i in range(method_count):
            method_info = self.generate_method_with_template(class_name, i)
            methods.append(method_info)
        
        # 生成文件
        return self.generate_files(class_name, members=members, methods=methods)
