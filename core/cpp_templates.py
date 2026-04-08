"""
C++ 原生模板模块
完全独立于 Objective-C 的 C++ 代码模板系统
"""

import random
from typing import Dict, List, Any


# C++ 方法模板定义（完全原生 C++ 语法）
CPP_METHOD_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "simple_void": {
        "description": "简单无返回值方法",
        "signature_format": "void {method_name}()",
        "body_template": [
            "// Simple void method",
            'std::cout << __FUNCTION__ << " called" << std::endl;'
        ],
        "applicable_types": ["manager", "service", "processor", "storage", "factory", "observer", "adapter"],
        "complexity": 1
    },
    "simple_return": {
        "description": "简单有返回值方法",
        "signature_format": "{return_type} {method_name}()",
        "body_template": [
            "// Simple return method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "return {default_value};"
        ],
        "applicable_types": ["manager", "service", "processor", "storage", "factory", "observer", "adapter"],
        "complexity": 1
    },
    "async_method": {
        "description": "异步方法（C++11 std::async）",
        "signature_format": "void {method_name}(std::function<void()> callback)",
        "body_template": [
            "// Async method with callback",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "std::async(std::launch::async, [this, callback]() {",
            "    // Perform async operation",
            "    // Background task here",
            "    if (callback) { callback(); }",
            "});"
        ],
        "applicable_types": ["manager", "service", "processor", "storage"],
        "complexity": 3
    },
    "callback_method": {
        "description": "回调方法",
        "signature_format": "void {method_name}(std::function<void(void*)> callback)",
        "body_template": [
            "// Callback method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "void* result = this->processResult();",
            "if (callback) { callback(result); }"
        ],
        "applicable_types": ["manager", "service", "factory", "observer"],
        "complexity": 2
    },
    "error_handling": {
        "description": "错误处理方法",
        "signature_format": "bool {method_name}(std::string& error)",
        "body_template": [
            "// Error handling method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "error.clear();",
            "bool success = true;",
            "if (!success) {",
            '    error = "Operation failed";',
            "}",
            "return success;"
        ],
        "applicable_types": ["manager", "service", "processor", "storage", "factory"],
        "complexity": 3
    },
    "error_handling_ptr": {
        "description": "错误处理方法（指针版本）",
        "signature_format": "bool {method_name}(std::string* error)",
        "body_template": [
            "// Error handling method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "if (error) { *error = \"\"; }",
            "bool success = true;",
            "if (!success) {",
            '    if (error) { *error = "Operation failed"; }',
            "}",
            "return success;"
        ],
        "applicable_types": ["manager", "service", "processor", "storage", "factory"],
        "complexity": 3
    },
    "factory_method": {
        "description": "工厂方法",
        "signature_format": "static std::unique_ptr<{class_name}> {method_name}()",
        "body_template": [
            "// Factory method",
            "auto instance = std::make_unique<{class_name}>();",
            "instance->setup();",
            "return instance;"
        ],
        "applicable_types": ["factory", "builder", "manager"],
        "complexity": 2
    },
    "singleton_access": {
        "description": "单例访问方法（C++11 线程安全）",
        "signature_format": "static {class_name}& sharedInstance()",
        "body_template": [
            "// Thread-safe singleton (C++11)",
            "static {class_name} instance;",
            "return instance;"
        ],
        "applicable_types": ["manager", "service", "storage", "registry"],
        "complexity": 2
    },
    "cache_logic": {
        "description": "缓存逻辑方法",
        "signature_format": "void* {method_name}(const std::string& key)",
        "body_template": [
            "// Cache logic method",
            'std::cout << __FUNCTION__ << " called with key: " << key << std::endl;',
            "auto it = cache_.find(key);",
            "if (it != cache_.end()) { return it->second; }",
            "void* value = this->fetchValue(key);",
            "cache_[key] = value;",
            "return value;"
        ],
        "applicable_types": ["storage", "cache", "service", "manager"],
        "complexity": 3
    },
    "cache_logic_string": {
        "description": "缓存逻辑方法（字符串返回值）",
        "signature_format": "std::string {method_name}(const std::string& key)",
        "body_template": [
            "// Cache logic method",
            'std::cout << __FUNCTION__ << " called with key: " << key << std::endl;',
            "auto it = cache_.find(key);",
            "if (it != cache_.end()) { return it->second; }",
            "std::string value = this->fetchValue(key);",
            "cache_[key] = value;",
            "return value;"
        ],
        "applicable_types": ["storage", "cache", "service", "manager"],
        "complexity": 3
    },
    "validation_logic": {
        "description": "验证逻辑方法",
        "signature_format": "bool {method_name}(const void* value)",
        "body_template": [
            "// Validation logic method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "if (value == nullptr) { return false; }",
            "return true;"
        ],
        "applicable_types": ["processor", "validator", "manager", "service"],
        "complexity": 2
    },
    "validation_string": {
        "description": "字符串验证方法",
        "signature_format": "bool {method_name}(const std::string& value)",
        "body_template": [
            "// Validation logic method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "if (value.empty()) { return false; }",
            "return true;"
        ],
        "applicable_types": ["processor", "validator", "manager", "service"],
        "complexity": 2
    },
    "logging_method": {
        "description": "日志记录方法",
        "signature_format": "void {method_name}(const std::string& message)",
        "body_template": [
            "// Logging method",
            'std::string timestamp = "[INFO]";',
            'std::cout << timestamp << ": " << message << std::endl;',
            "this->writeLog(message);"
        ],
        "applicable_types": ["logger", "monitor", "observer", "service"],
        "complexity": 2
    },
    "chainable_method": {
        "description": "链式调用方法",
        "signature_format": "{class_name}& {method_name}(void* value)",
        "body_template": [
            "// Chainable method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "currentValue_ = value;",
            "return *this;"
        ],
        "applicable_types": ["builder", "factory", "adapter"],
        "complexity": 1
    },
    "chainable_method_string": {
        "description": "链式调用方法（字符串参数）",
        "signature_format": "{class_name}& {method_name}(const std::string& value)",
        "body_template": [
            "// Chainable method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "currentValue_ = value;",
            "return *this;"
        ],
        "applicable_types": ["builder", "factory", "adapter"],
        "complexity": 1
    },
    "loop_processing": {
        "description": "循环处理方法",
        "signature_format": "void {method_name}(const std::vector<void*>& array)",
        "body_template": [
            "// Loop processing method",
            'std::cout << __FUNCTION__ << " called with array size: " << array.size() << std::endl;',
            "for (const auto& obj : array) {",
            "    this->processObject(obj);",
            "}"
        ],
        "applicable_types": ["processor", "manager", "service"],
        "complexity": 3
    },
    "loop_processing_int": {
        "description": "循环处理方法（索引版本）",
        "signature_format": "void {method_name}(int count)",
        "body_template": [
            "// Loop processing method",
            'std::cout << __FUNCTION__ << " called with count: " << count << std::endl;',
            "for (int i = 0; i < count; i++) {",
            "    // Process item",
            "    if (i % 2 == 0) {",
            '        std::cout << "Processing even index: " << i << std::endl;',
            "    }",
            "}"
        ],
        "applicable_types": ["processor", "manager", "service"],
        "complexity": 3
    },
    "condition_handling": {
        "description": "条件处理方法",
        "signature_format": "std::string {method_name}(int type)",
        "body_template": [
            "// Condition handling method",
            'std::cout << __FUNCTION__ << " called with type: " << type << std::endl;',
            "switch (type) {",
            '    case 0: return "TypeA";',
            '    case 1: return "TypeB";',
            '    case 2: return "TypeC";',
            '    default: return "Unknown";',
            "}"
        ],
        "applicable_types": ["processor", "adapter", "factory"],
        "complexity": 2
    },
    "generic_method": {
        "description": "泛型方法",
        "signature_format": "std::vector<void*> {method_name}(const std::vector<void*>& items)",
        "body_template": [
            "// Generic method",
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            "std::vector<void*> result;",
            "for (const auto& item : items) {",
            "    result.push_back(this->transformItem(item));",
            "}",
            "return result;"
        ],
        "applicable_types": ["processor", "transformer", "factory"],
        "complexity": 2
    },
    "map_lookup": {
        "description": "Map 查找方法",
        "signature_format": "std::string {method_name}(const std::string& key)",
        "body_template": [
            "// Map lookup method",
            'std::cout << __FUNCTION__ << " called with key: " << key << std::endl;',
            "auto it = cache_.find(key);",
            'if (it != cache_.end()) { return it->second; }',
            'return "";'
        ],
        "applicable_types": ["storage", "registry", "manager", "service"],
        "complexity": 2
    },
    "vector_operation": {
        "description": "Vector 操作方法",
        "signature_format": "void {method_name}(const std::vector<std::string>& items)",
        "body_template": [
            "// Vector operation method",
            'std::cout << __FUNCTION__ << " called with " << items.size() << " items" << std::endl;',
            "for (const auto& item : items) {",
            "    this->processItem(item);",
            "}"
        ],
        "applicable_types": ["processor", "manager", "service"],
        "complexity": 2
    }
}


# C++ 代码块模板库（用于增加代码多样性）
CPP_CODE_BLOCKS: Dict[str, List[str]] = {
    "log": [
        'std::cout << __FUNCTION__ << " called" << std::endl;',
        'std::cout << "[DEBUG] " << __FUNCTION__ << std::endl;',
        'std::cerr << "[ERROR] " << __FUNCTION__ << std::endl;',
        '// Logging: __FUNCTION__',
        'std::cout << "[VERBOSE] " << __FUNCTION__ << std::endl;',
    ],
    "validation": [
        "if (message.empty()) { return false; }",
        "if (ptr_ == nullptr) { return false; }",
        "if (count_ > maxCount_) { return false; }",
        "if (index_ < 0 || index_ >= size_) { return false; }",
        "if (!initialized_) { return false; }",
    ],
    "nullCheck": [
        "if (ptr_ == nullptr) { return; }",
        "if (obj_ == nullptr) { return false; }",
        "if (!this) { return; }",
        "if (cache_.empty()) { return; }",
    ],
    "errorHandling": [
        "try { } catch (const std::exception& e) { std::cerr << e.what() << std::endl; }",
        'if (error) { *error = "Operation failed"; return false; }',
        "throw std::runtime_error(\"Error occurred\");",
        "if (result != 0) { return false; }",
    ],
    "async": [
        "std::async(std::launch::async, [this]() { /* async operation */ });",
        "std::thread([this]() { /* background task */ }).detach();",
        "// TODO: Implement async operation",
        "std::future<void> future = std::async(std::launch::async, [this]() { });",
    ],
    "cache": [
        "auto it = cache_.find(key);",
        "if (it != cache_.end()) { return it->second; }",
        "cache_[key] = value;",
        "// Cache miss - fetch value",
        "if (cache_.size() > MAX_CACHE_SIZE) { cache_.clear(); }",
    ],
    "loop": [
        "for (int i = 0; i < count; i++) { }",
        "for (const auto& item : container) { }",
        "std::for_each(container.begin(), container.end(), [](const auto& item) { });",
        "for (auto it = container.begin(); it != container.end(); ++it) { }",
    ],
    "condition": [
        "if (condition) { } else { }",
        "switch (state) { case 0: break; default: break; }",
        "if (value > threshold) { }",
        "if (flag_) { }",
    ],
    "singleton": [
        "static ClassName& sharedInstance() {\n    static ClassName instance;\n    return instance;\n}",
        "static std::shared_ptr<ClassName> getInstance() {\n    static auto instance = std::make_shared<ClassName>();\n    return instance;\n}",
    ],
    "factory": [
        "static std::unique_ptr<ClassName> create() {\n    return std::make_unique<ClassName>();\n}",
        "static ClassName* createInstance() {\n    return new ClassName();\n}",
    ],
    "member_init": [
        "data_ = {};",
        "initialized_ = false;",
        "count_ = 0;",
        'name_ = "";',
        "ptr_ = nullptr;",
    ]
}


class CppTemplateEngine:
    """C++ 模板引擎类 - 完全独立于 Objective-C"""
    
    def __init__(self):
        """初始化 C++ 模板引擎"""
        self.templates = CPP_METHOD_TEMPLATES
        self.code_blocks = CPP_CODE_BLOCKS
        self.rng = random.Random()
    
    def get_template(self, template_name: str) -> Dict[str, Any]:
        """获取指定名称的模板"""
        return self.templates.get(template_name, self.templates["simple_void"])
    
    def get_code_block(self, block_type: str) -> str:
        """获取指定类型的代码块"""
        if block_type in self.code_blocks:
            return self.rng.choice(self.code_blocks[block_type])
        return "// Unknown code block type"
    
    def get_applicable_templates(self, class_type: str) -> List[Dict[str, Any]]:
        """获取适用于指定类类型的所有模板"""
        applicable = []
        for template in self.templates.values():
            if class_type in template.get("applicable_types", []):
                applicable.append(template)
        return applicable if applicable else [self.templates["simple_void"]]
    
    def select_template(self, class_type: str, diversity_level: str = "high",
                       seed: int = None) -> Dict[str, Any]:
        """根据类类型和多样性级别选择模板"""
        if seed is not None:
            self.rng.seed(seed)
        
        applicable = self.get_applicable_templates(class_type)
        
        if diversity_level == "low":
            # 低多样性：优先选择简单模板
            simple = [t for t in applicable if t.get("complexity", 1) <= 2]
            if simple:
                return self.rng.choice(simple)
        elif diversity_level == "medium":
            # 中等多样性：按复杂度加权
            weights = [max(1, 4 - t.get("complexity", 1)) for t in applicable]
            return self.rng.choices(applicable, weights=weights)[0]
        
        # 高多样性或默认：完全随机
        return self.rng.choice(applicable)
    
    def generate_signature(self, template: Dict[str, Any], method_name: str,
                          return_type: str = "void", class_name: str = "") -> str:
        """生成方法签名"""
        signature_format = template.get("signature_format", "void {method_name}()")
        signature = signature_format.replace("{method_name}", method_name)
        signature = signature.replace("{return_type}", return_type)
        signature = signature.replace("{class_name}", class_name)
        return signature
    
    def generate_body(self, template: Dict[str, Any], return_type: str = "void",
                     class_name: str = "", enable_code_blocks: bool = True) -> List[str]:
        """生成方法体"""
        body_template = template.get("body_template", [])
        body_lines = list(body_template)
        
        # 处理占位符
        body_lines = [line.replace("{class_name}", class_name) for line in body_lines]
        body_lines = [line.replace("{default_value}", self._get_default_value(return_type)) 
                     for line in body_lines]
        
        # 添加额外代码块增加多样性
        if enable_code_blocks and len(body_lines) > 1:
            block_type = self.rng.choice(["log", "validation", "nullCheck"])
            extra_line = self.get_code_block(block_type)
            body_lines.insert(1, extra_line)
        
        return body_lines
    
    def _get_default_value(self, return_type: str) -> str:
        """获取类型的默认值"""
        if return_type == "void":
            return ""
        elif return_type in ["int", "long", "short", "size_t"]:
            return "0"
        elif return_type in ["float", "double"]:
            return "0.0f"
        elif return_type == "bool":
            return "false"
        elif return_type == "std::string":
            return '""'
        elif return_type.startswith("std::vector"):
            return "{}"
        elif return_type.startswith("std::map"):
            return "{}"
        elif return_type.endswith("*") or return_type == "void*":
            return "nullptr"
        else:
            return "{}"
