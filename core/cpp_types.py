"""
C++ 类型系统模块
完全独立于 Objective-C 的 C++ 类型定义和转换系统
"""

from typing import Dict, List, Any, Optional, Tuple
import random


# C++ 基本类型定义
CPP_PRIMITIVE_TYPES: Dict[str, List[str]] = {
    "string": ["std::string", "const std::string&"],
    "number": ["int", "long", "double", "float", "size_t"],
    "boolean": ["bool"],
    "void": ["void"],
    "pointer": ["void*", "const void*"],
}


# C++ 容器类型定义
CPP_CONTAINER_TYPES: Dict[str, str] = {
    "vector": "std::vector<void*>",
    "vector_string": "std::vector<std::string>",
    "vector_int": "std::vector<int>",
    "map": "std::map<std::string, void*>",
    "map_string": "std::map<std::string, std::string>",
    "set": "std::set<void*>",
    "set_string": "std::set<std::string>",
    "queue": "std::queue<void*>",
    "stack": "std::stack<void*>",
}


# C++ 函数类型定义
CPP_FUNCTION_TYPES: Dict[str, str] = {
    "void_callback": "std::function<void()>",
    "value_callback": "std::function<void(void*)>",
    "string_callback": "std::function<void(const std::string&)>",
    "bool_callback": "std::function<void(bool)>",
    "error_callback": "std::function<void(const std::string*)>",
    "predicate": "std::function<bool(const void*)>",
    "transformer": "std::function<void*(const void*)>",
}


# 类型默认值映射
CPP_DEFAULT_VALUES: Dict[str, str] = {
    # 基本类型
    "void": "",
    "int": "0",
    "long": "0L",
    "short": "0",
    "float": "0.0f",
    "double": "0.0",
    "size_t": "0",
    "bool": "false",
    "char": "'\\0'",
    
    # 字符串类型
    "std::string": '""',
    "const std::string&": '""',
    "char*": "nullptr",
    "const char*": "nullptr",
    
    # 指针类型
    "void*": "nullptr",
    "const void*": "nullptr",
    
    # 容器类型
    "std::vector<void*>": "{}",
    "std::vector<std::string>": "{}",
    "std::vector<int>": "{}",
    "std::map<std::string, void*>": "{}",
    "std::map<std::string, std::string>": "{}",
    "std::set<void*>": "{}",
    "std::set<std::string>": "{}",
    
    # 函数类型
    "std::function<void()>": "nullptr",
    "std::function<void(void*)>": "nullptr",
    "std::function<void(const std::string&)>": "nullptr",
    "std::function<bool(const void*)>": "nullptr",
    
    # 智能指针
    "std::unique_ptr<void>": "nullptr",
    "std::shared_ptr<void>": "nullptr",
    "std::weak_ptr<void>": "{}",
}


# 类型头文件映射（生成 #include 时使用）
CPP_TYPE_INCLUDES: Dict[str, str] = {
    "std::string": "<string>",
    "std::vector": "<vector>",
    "std::map": "<map>",
    "std::set": "<set>",
    "std::queue": "<queue>",
    "std::stack": "<stack>",
    "std::function": "<functional>",
    "std::unique_ptr": "<memory>",
    "std::shared_ptr": "<memory>",
    "std::weak_ptr": "<memory>",
    "std::async": "<future>",
    "std::future": "<future>",
    "std::thread": "<thread>",
}


# 类型类别映射
CPP_TYPE_CATEGORIES: Dict[str, List[str]] = {
    "integral": ["int", "long", "short", "size_t", "char"],
    "floating": ["float", "double"],
    "string": ["std::string", "const std::string&", "char*", "const char*"],
    "boolean": ["bool"],
    "pointer": ["void*", "const void*"],
    "container": [
        "std::vector<void*>", "std::vector<std::string>", "std::vector<int>",
        "std::map<std::string, void*>", "std::map<std::string, std::string>",
        "std::set<void*>", "std::set<std::string>"
    ],
    "function": [
        "std::function<void()>", "std::function<void(void*)>",
        "std::function<void(const std::string&)>", "std::function<bool(const void*)>"
    ],
}


class CppTypeSystem:
    """C++ 类型系统类 - 完全独立于 Objective-C"""
    
    def __init__(self):
        """初始化 C++ 类型系统"""
        self.primitive_types = CPP_PRIMITIVE_TYPES
        self.container_types = CPP_CONTAINER_TYPES
        self.function_types = CPP_FUNCTION_TYPES
        self.default_values = CPP_DEFAULT_VALUES
        self.type_includes = CPP_TYPE_INCLUDES
        self.type_categories = CPP_TYPE_CATEGORIES
        self.rng = random.Random()
    
    def set_seed(self, seed: int):
        """设置随机种子"""
        self.rng.seed(seed)
    
    def get_type(self, category: str, specific_type: str = None) -> str:
        """
        获取指定类别的类型
        
        Args:
            category: 类型类别 (string/number/boolean/container/function/pointer)
            specific_type: 具体类型名称（可选）
            
        Returns:
            C++ 类型字符串
        """
        if specific_type:
            return specific_type
        
        if category == "string":
            return self.rng.choice(self.primitive_types["string"])
        elif category == "number":
            return self.rng.choice(self.primitive_types["number"])
        elif category == "boolean":
            return "bool"
        elif category == "pointer":
            return self.rng.choice(self.primitive_types["pointer"])
        elif category == "container":
            return self.rng.choice(list(self.container_types.values()))
        elif category == "function":
            return self.rng.choice(list(self.function_types.values()))
        elif category == "void":
            return "void"
        
        return "void"
    
    def get_default_value(self, type_name: str) -> str:
        """
        获取类型的默认值
        
        Args:
            type_name: 类型名称
            
        Returns:
            默认值字符串
        """
        # 直接匹配
        if type_name in self.default_values:
            return self.default_values[type_name]
        
        # 前缀匹配（用于模板类型）
        for known_type, default_value in self.default_values.items():
            if type_name.startswith(known_type):
                return default_value
        
        # 指针类型默认值
        if type_name.endswith("*"):
            return "nullptr"
        
        # 引用类型默认值
        if type_name.endswith("&"):
            base_type = type_name.replace("const ", "").replace("&", "").strip()
            return self.get_default_value(base_type)
        
        # 未知类型返回空初始化
        return "{}"
    
    def get_required_includes(self, types: List[str]) -> List[str]:
        """
        获取类型所需的头文件列表
        
        Args:
            types: 类型列表
            
        Returns:
            去重后的头文件列表
        """
        includes = set()
        
        for type_name in types:
            # 直接匹配
            if type_name in self.type_includes:
                includes.add(self.type_includes[type_name])
                continue
            
            # 前缀匹配
            for known_type, include in self.type_includes.items():
                if type_name.startswith(known_type):
                    includes.add(include)
                    break
        
        # 总是包含基础头文件
        includes.add("<iostream>")
        
        return sorted(list(includes))
    
    def is_pointer_type(self, type_name: str) -> bool:
        """判断是否为指针类型"""
        return type_name.endswith("*")
    
    def is_reference_type(self, type_name: str) -> bool:
        """判断是否为引用类型"""
        return type_name.endswith("&")
    
    def is_container_type(self, type_name: str) -> bool:
        """判断是否为容器类型"""
        return (type_name.startswith("std::vector") or 
                type_name.startswith("std::map") or
                type_name.startswith("std::set") or
                type_name.startswith("std::queue") or
                type_name.startswith("std::stack"))
    
    def is_function_type(self, type_name: str) -> bool:
        """判断是否为函数类型"""
        return type_name.startswith("std::function<")
    
    def is_primitive_type(self, type_name: str) -> bool:
        """判断是否为基本类型"""
        primitive_bases = ["int", "long", "short", "float", "double", "bool", "char", "size_t", "void"]
        return type_name in primitive_bases
    
    def get_base_type(self, type_name: str) -> str:
        """
        获取类型的基础类型（去除 const、引用等修饰）
        
        Args:
            type_name: 类型名称
            
        Returns:
            基础类型
        """
        base = type_name
        base = base.replace("const ", "")
        base = base.replace("&", "")
        base = base.replace("*", "")
        return base.strip()
    
    def generate_param_declaration(self, name: str, type_name: str, 
                                   is_const: bool = False) -> str:
        """
        生成参数声明
        
        Args:
            name: 参数名
            type_name: 类型名
            is_const: 是否为 const
            
        Returns:
            参数声明字符串
        """
        # 基本类型直接传值
        if self.is_primitive_type(type_name):
            return f"{type_name} {name}"
        
        # 字符串类型使用 const 引用
        if type_name == "std::string":
            return f"const std::string& {name}"
        
        # 容器类型使用 const 引用
        if self.is_container_type(type_name):
            return f"const {type_name}& {name}"
        
        # 函数类型直接声明
        if self.is_function_type(type_name):
            return f"{type_name} {name}"
        
        # 指针类型
        if self.is_pointer_type(type_name):
            return f"{type_name} {name}"
        
        # 其他类型使用 const 引用
        if is_const:
            return f"const {type_name}& {name}"
        return f"{type_name} {name}"
    
    def generate_member_declaration(self, name: str, type_name: str,
                                    access: str = "private") -> str:
        """
        生成成员变量声明
        
        Args:
            name: 成员名
            type_name: 类型名
            access: 访问修饰符 (private/protected/public)
            
        Returns:
            成员声明字符串
        """
        return f"    {access}:\n    {type_name} {name};"
    
    def generate_method_signature(self, name: str, return_type: str,
                                  params: List[Tuple[str, str]] = None,
                                  is_const: bool = False,
                                  is_static: bool = False) -> str:
        """
        生成方法签名
        
        Args:
            name: 方法名
            return_type: 返回类型
            params: 参数列表 [(type, name), ...]
            is_const: 是否为 const 方法
            is_static: 是否为静态方法
            
        Returns:
            方法签名字符串
        """
        parts = []
        
        if is_static:
            parts.append("static")
        
        parts.append(return_type)
        
        # 构建参数列表
        param_strs = []
        if params:
            for param_type, param_name in params:
                param_strs.append(self.generate_param_declaration(param_name, param_type))
        
        signature = " ".join(parts) + f" {name}({', '.join(param_strs)})"
        
        if is_const:
            signature += " const"
        
        return signature
    
    def get_random_return_type(self, allow_void: bool = True) -> str:
        """获取随机返回类型"""
        candidates = ["void", "bool", "int", "std::string", "void*"]
        if not allow_void:
            candidates = candidates[1:]
        return self.rng.choice(candidates)
    
    def get_random_param_type(self) -> Tuple[str, str]:
        """获取随机参数类型和名称"""
        type_categories = [
            ("std::string", "key"),
            ("std::string", "value"),
            ("std::string", "message"),
            ("int", "count"),
            ("int", "type"),
            ("int", "index"),
            ("bool", "flag"),
            ("void*", "data"),
            ("void*", "ptr"),
            ("std::function<void()>", "callback"),
            ("std::function<void(void*)>", "callback"),
            ("const std::vector<void*>&", "items"),
            ("const std::vector<std::string>&", "strings"),
        ]
        return self.rng.choice(type_categories)
