"""
模板引擎模块
负责根据类类型选择模板，生成方法签名和实现
提供代码块多样性
"""

import random
from typing import Dict, List, Any, Optional, Tuple


class TemplateEngine:
    """模板引擎类"""
    
    # 类类型映射
    CLASS_TYPE_MAPPING = {
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
    
    # 方法模板定义（15 种）
    METHOD_TEMPLATES = {
        "simple_void": {
            "description": "简单无返回值方法",
            "signature_format": "- (void){method_name};",
            "body_template": ["// Simple void method", "NSLog(@\"%s called\", __func__);"],
            "applicable_types": ["manager", "service", "processor", "storage", "factory", "observer", "adapter"],
            "complexity": 1
        },
        "simple_return": {
            "description": "简单有返回值方法",
            "signature_format": "- ({return_type}){method_name};",
            "body_template": ["// Simple return method", "NSLog(@\"%s called\", __func__);", "return {default_value};"],
            "applicable_types": ["manager", "service", "processor", "storage", "factory", "observer", "adapter"],
            "complexity": 1
        },
        "async_method": {
            "description": "异步方法",
            "signature_format": "- (void){method_name}WithCompletion:(void (^)(NSError * _Nullable))completion;",
            "body_template": [
                "// Async method with completion",
                "NSLog(@\"%s called\", __func__);",
                "dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{",
                "    // Perform async operation",
                "    NSError *error = nil;",
                "    dispatch_async(dispatch_get_main_queue(), ^{",
                "        if (completion) { completion(error); }",
                "    });"
            ],
            "applicable_types": ["manager", "service", "processor", "storage"],
            "complexity": 3
        },
        "block_callback": {
            "description": "Block 回调方法",
            "signature_format": "- (void){method_name}WithBlock:(void (^)(id result))block;",
            "body_template": [
                "// Block callback method",
                "NSLog(@\"%s called\", __func__);",
                "id result = [self processResult];",
                "if (block) { block(result); }"
            ],
            "applicable_types": ["manager", "service", "factory", "observer"],
            "complexity": 2
        },
        "error_handling": {
            "description": "错误处理方法",
            "signature_format": "- (BOOL){method_name}WithError:(NSError * _Nullable __autoreleasing *)error;",
            "body_template": [
                "// Error handling method",
                "NSLog(@\"%s called\", __func__);",
                "if (error) { *error = nil; }",
                "BOOL success = YES;",
                "if (!success) {",
                "if (error) {",
                "*error = [NSError errorWithDomain:@\"com.error.domain\" code:-1 userInfo:@{NSLocalizedDescriptionKey: @\"Operation failed\"}];",
                "}",
                "}",
                "return success;"
            ],
            "applicable_types": ["manager", "service", "processor", "storage", "factory"],
            "complexity": 3
        },
        "delegate_pattern": {
            "description": "代理模式方法",
            "signature_format": "- (void){method_name};",
            "body_template": [
                "// Delegate pattern method",
                "NSLog(@\"%s called\", __func__);",
                "if ([self.delegate respondsToSelector:@selector(didCompleteOperation:)]) {",
                "    [self.delegate didCompleteOperation:self];",
                "}"
            ],
            "applicable_types": ["manager", "service", "observer", "adapter"],
            "complexity": 2
        },
        "factory_method": {
            "description": "工厂方法",
            "signature_format": "+ (instancetype){method_name};",
            "body_template": [
                "// Factory method",
                "instancetype instance = [[self alloc] init];",
                "[instance setup];",
                "return instance;"
            ],
            "applicable_types": ["factory", "builder", "manager"],
            "complexity": 2
        },
        "singleton_access": {
            "description": "单例访问方法",
            "signature_format": "+ (instancetype)sharedInstance;",
            "body_template": [
                "// Singleton access",
                "static instancetype sharedInstance = nil;",
                "static dispatch_once_t onceToken;",
                "dispatch_once(&onceToken, ^{",
                "    sharedInstance = [[self alloc] init];",
                "});",
                "return sharedInstance;"
            ],
            "applicable_types": ["manager", "service", "storage", "registry"],
            "complexity": 2
        },
        "cache_logic": {
            "description": "缓存逻辑方法",
            "signature_format": "- (id){method_name}ForKey:(NSString *)key;",
            "body_template": [
                "// Cache logic method",
                "NSLog(@\"%s called with key: %@\", __func__, key);",
                "NSString *cacheKey = [NSString stringWithFormat:@\"%@_%@\", NSStringFromClass([self class]), key];",
                "id cached = [self.cache objectForKey:cacheKey];",
                "if (cached) { return cached; }",
                "id value = [self fetchValueForKey:key];",
                "if (value) { [self.cache setObject:value forKey:cacheKey]; }",
                "return value;"
            ],
            "applicable_types": ["storage", "cache", "service", "manager"],
            "complexity": 3
        },
        "validation_logic": {
            "description": "验证逻辑方法",
            "signature_format": "- (BOOL)validate{method_name}:(id)value;",
            "body_template": [
                "// Validation logic method",
                "NSLog(@\"%s called\", __func__);",
                "if (value == nil) { return NO; }",
                "if (![value isKindOfClass:[NSString class]]) { return NO; }",
                "if ([(NSString *)value length] == 0) { return NO; }",
                "return YES;"
            ],
            "applicable_types": ["processor", "validator", "manager", "service"],
            "complexity": 2
        },
        "logging_method": {
            "description": "日志记录方法",
            "signature_format": "- (void){method_name}WithMessage:(NSString *)message;",
            "body_template": [
                "// Logging method",
                "NSString *timestamp = [NSDateFormatter localizedStringFromDate:[NSDate date] dateStyle:NSDateFormatterMediumStyle timeStyle:NSDateFormatterMediumStyle];",
                "NSString *logMessage = [NSString stringWithFormat:@\"[%@] %@: %@\", timestamp, NSStringFromClass([self class]), message];",
                "NSLog(@\"%@\", logMessage);",
                "[self writeLog:message];"
            ],
            "applicable_types": ["logger", "monitor", "observer", "service"],
            "complexity": 2
        },
        "chainable_method": {
            "description": "链式调用方法",
            "signature_format": "- (instancetype){method_name}:(id)value;",
            "body_template": [
                "// Chainable method",
                "NSLog(@\"%s called\", __func__);",
                "_currentValue = value;",
                "return self;"
            ],
            "applicable_types": ["builder", "factory", "adapter"],
            "complexity": 1
        },
        "loop_processing": {
            "description": "循环处理方法",
            "signature_format": "- (void){method_name}WithArray:(NSArray *)array;",
            "body_template": [
                "// Loop processing method",
                "NSLog(@\"%s called with array count: %lu\", __func__, (unsigned long)array.count);",
                "for (id obj in array) {",
                "[self processObject:obj];",
                "if ([obj respondsToSelector:@selector(validate)]) {",
                "if (![obj validate]) { continue; }",
                "}",
                "}"
            ],
            "applicable_types": ["processor", "manager", "service"],
            "complexity": 3
        },
        "condition_handling": {
            "description": "条件处理方法",
            "signature_format": "- (id){method_name}WithType:(NSInteger)type;",
            "body_template": [
                "// Condition handling method",
                "NSLog(@\"%s called with type: %ld\", __func__, (long)type);",
                "switch (type) {",
                "case 0: return @\"TypeA\";",
                "case 1: return @\"TypeB\";",
                "case 2: return @\"TypeC\";",
                "default: return @\"Unknown\";",
                "}"
            ],
            "applicable_types": ["processor", "adapter", "factory"],
            "complexity": 2
        },
        "generic_method": {
            "description": "泛型方法",
            "signature_format": "- (NSArray<T> *){method_name}WithItems:(NSArray<T> *)items;",
            "body_template": [
                "// Generic method",
                "NSLog(@\"%s called\", __func__);",
                "NSMutableArray *result = [NSMutableArray arrayWithCapacity:items.count];",
                "for (id item in items) {",
                "    [result addObject:[self transformItem:item]];",
                "}",
                "return result;"
            ],
            "applicable_types": ["processor", "transformer", "factory"],
            "complexity": 2
        }
    }
    
    # 代码块模板库
    CODE_BLOCK_TEMPLATES = {
        "log": [
            "NSLog(@\"[DEBUG] %@ called\", NSStringFromSelector(_cmd));",
            "os_log(OS_LOG_DEFAULT, \"[INFO] %{public}s\", __func__);",
            "NSLog(@\"[VERBOSE] Value: %@\", value);",
            "NSAssert(value != nil, @\"Value must not be nil\");",
            "NSParameterAssert(param != nil);",
        ],
        "validation": [
            "if (value == nil) { return NO; }",
            "NSParameterAssert(param != nil);",
            "if (![value isKindOfClass:[NSString class]]) { return NO; }",
            "if (value.length == 0) { return NO; }",
            "if (count > maxCount) { return NO; }",
        ],
        "nullCheck": [
            "if (value == nil) { return; }",
            "if (object == nil) { return NO; }",
            "NSParameterAssert(object != nil);",
            "if (!self) { return; }",
        ],
        "errorHandling": [
            "NSError *error = nil;",
            "if (error) { *error = [NSError errorWithDomain:@\"com.error\" code:-1 userInfo:nil]; return NO; }",
            "dispatch_async(dispatch_get_main_queue(), ^{ completionHandler(nil, error); });",
        ],
        "async": [
            "dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{ });",
            "dispatch_async(dispatch_get_main_queue(), ^{ });",
            "NSOperationQueue *queue = [[NSOperationQueue alloc] init];",
        ],
        "cache": [
            "NSString *key = [NSString stringWithFormat:@\"%@_%@\", NSStringFromClass([self class]), identifier];",
            "id cached = [self.cache objectForKey:key];",
            "[self.cache setObject:object forKey:key];",
            "if (cached) { return cached; }",
        ],
        "loop": [
            "for (int i = 0; i < count; i++) {\n// Process item\n}",
            "for (id obj in array) {\n[self processObject:obj];\n}",
            "[array enumerateObjectsUsingBlock:^(id obj, NSUInteger idx, BOOL *stop) {\n// Process item\n}];",
        ],
        "condition": [
            "if (condition) {\n// Handle condition\n} else {\n// Handle else\n}",
            "switch (state) {\ncase StateA:\nbreak;\ndefault:\nbreak;\n}",
            "if ([value isKindOfClass:[NSString class]]) {\n// Process string\n}",
        ]
    }
    
    # C++ 代码块模板库（原生 C++ 语法）
    CPP_CODE_BLOCK_TEMPLATES = {
        "log": [
            'std::cout << __FUNCTION__ << " called" << std::endl;',
            'std::cout << "[DEBUG] " << __FUNCTION__ << std::endl;',
            'std::cerr << "[ERROR] " << __FUNCTION__ << std::endl;',
            'assert(value != nullptr);',
            '// Logging: __FUNCTION__',
        ],
        "validation": [
            "if (value.empty()) { return false; }",
            "if (ptr == nullptr) { return false; }",
            "if (count > maxCount) { return false; }",
            "if (index < 0 || index >= size) { return false; }",
        ],
        "nullCheck": [
            "if (ptr == nullptr) { return; }",
            "if (object == nullptr) { return false; }",
            "if (!this) { return; }",
        ],
        "errorHandling": [
            "try { } catch (const std::exception& e) { std::cerr << e.what() << std::endl; }",
            "if (error) { *error = \"Operation failed\"; return false; }",
            "throw std::runtime_error(\"Error occurred\");",
        ],
        "async": [
            "std::async(std::launch::async, [this]() { /* async operation */ });",
            "std::thread([this]() { /* background task */ }).detach();",
            "// TODO: Implement async operation",
        ],
        "cache": [
            "auto it = cache.find(key);",
            "if (it != cache.end()) { return it->second; }",
            "cache[key] = value;",
            "// Cache miss - fetch value",
        ],
        "loop": [
            "for (int i = 0; i < count; i++) {\n// Process item\n}",
            "for (const auto& item : container) {\n// Process item\n}",
            "std::for_each(container.begin(), container.end(), [](const auto& item) {\n// Process item\n});",
        ],
        "condition": [
            "if (condition) {\n// Handle condition\n} else {\n// Handle else\n}",
            "switch (state) {\ncase 0:\nbreak;\ndefault:\nbreak;\n}",
            "if (typeid(value) == typeid(int)) {\n// Process int\n}",
        ],
        "singleton": [
            "static ClassName& sharedInstance() {\n    static ClassName instance;\n    return instance;\n}",
            "static std::shared_ptr<ClassName> getInstance() {\n    static auto instance = std::make_shared<ClassName>();\n    return instance;\n}",
        ],
        "factory": [
            "static std::unique_ptr<ClassName> create() {\n    return std::make_unique<ClassName>();\n}",
            "static ClassName* createInstance() {\n    return new ClassName();\n}",
        ]
    }
    
    # C++ 类型映射表
    CPP_TYPE_MAPPING = {
        "NSString *": "std::string",
        "NSArray *": "std::vector<void*>",
        "NSMutableArray *": "std::vector<void*>",
        "NSDictionary *": "std::map<std::string, void*>",
        "NSMutableDictionary *": "std::map<std::string, void*>",
        "BOOL": "bool",
        "instancetype": "ClassName*",
        "id": "void*",
        "NSInteger": "int",
        "NSUInteger": "size_t",
        "CGFloat": "double",
        "void (^)(id)": "std::function<void(void*)>",
        "void (^)(NSError * _Nullable)": "std::function<void(const std::string*)>",
        "NSError **": "std::string*",
        "int": "int",
        "float": "float",
        "double": "double",
        "long": "long",
        "short": "short",
        "size_t": "size_t",
        "void": "void",
        "bool": "bool",
    }
    
    # C++ 方法模板定义
    CPP_METHOD_TEMPLATES = {
        "simple_void": {
            "description": "简单无返回值方法",
            "signature_format": "void {method_name}()",
            "body_template": ["// Simple void method", 'std::cout << __FUNCTION__ << " called" << std::endl;'],
            "applicable_types": ["manager", "service", "processor", "storage", "factory", "observer", "adapter"],
            "complexity": 1
        },
        "simple_return": {
            "description": "简单有返回值方法",
            "signature_format": "{return_type} {method_name}()",
            "body_template": ["// Simple return method", 'std::cout << __FUNCTION__ << " called" << std::endl;', "return {default_value};"],
            "applicable_types": ["manager", "service", "processor", "storage", "factory", "observer", "adapter"],
            "complexity": 1
        },
        "async_method": {
            "description": "异步方法",
            "signature_format": "void {method_name}(std::function<void(const std::string*)> callback)",
            "body_template": [
                "// Async method with callback",
                'std::cout << __FUNCTION__ << " called" << std::endl;',
                "std::async(std::launch::async, [this, callback]() {",
                "    // Perform async operation",
                "    std::string error;",
                "    if (callback) { callback(&error); }",
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
            "signature_format": "bool {method_name}(std::string* error)",
            "body_template": [
                "// Error handling method",
                'std::cout << __FUNCTION__ << " called" << std::endl;',
                "if (error) { *error = \"\"; }",
                "bool success = true;",
                "if (!success) {",
                "    if (error) {",
                '        *error = "Operation failed";',
                "    }",
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
            "description": "单例访问方法",
            "signature_format": "static {class_name}& sharedInstance()",
            "body_template": [
                "// Singleton access",
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
            "signature_format": "{class_name}*& {method_name}(void* value)",
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
        "condition_handling": {
            "description": "条件处理方法",
            "signature_format": "std::string {method_name}(int type)",
            "body_template": [
                "// Condition handling method",
                'std::cout << __FUNCTION__ << " called with type: " << type << std::endl;',
                "switch (type) {",
                "    case 0: return \"TypeA\";",
                "    case 1: return \"TypeB\";",
                "    case 2: return \"TypeC\";",
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
        }
    }
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        """
        初始化模板引擎
        
        Args:
            vocabulary: 词库配置
        """
        self.vocabulary = vocabulary or {}
        self.random = random.Random()
    
    def set_seed(self, seed: int):
        """设置随机种子"""
        self.random.seed(seed)
    
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
        
        # 默认返回 manager 类型
        return "manager"
    
    def select_method_template(self, class_type: str, method_index: int = 0, diversity_level: str = "high") -> Dict[str, Any]:
        """
        根据类类型选择模板
        
        Args:
            class_type: 类类型
            method_index: 方法索引
            diversity_level: 多样性级别 (low/medium/high)
            
        Returns:
            选中的方法模板
        """
        # 获取适用于该类类型的模板
        applicable_templates = []
        for template_name, template in self.METHOD_TEMPLATES.items():
            if class_type in template.get("applicable_types", []):
                applicable_templates.append((template_name, template))
        
        if not applicable_templates:
            # 如果没有适用的模板，返回默认模板
            return self.METHOD_TEMPLATES["simple_void"]
        
        # 根据多样性级别选择模板
        if diversity_level == "low":
            # 低多样性：优先选择简单模板
            simple_templates = [(n, t) for n, t in applicable_templates if t.get("complexity", 1) <= 2]
            if simple_templates:
                return self.random.choice(simple_templates)[1]
            return self.random.choice(applicable_templates)[1]
        
        elif diversity_level == "medium":
            # 中等多样性：按复杂度加权选择
            weights = [max(1, 4 - t.get("complexity", 1)) for _, t in applicable_templates]
            return self.random.choices(applicable_templates, weights=weights)[0][1]
        
        else:  # high
            # 高多样性：完全随机选择
            return self.random.choice(applicable_templates)[1]
    
    def generate_method_signature(self, method_name: str, template: Dict[str, Any], return_type: str = "void") -> str:
        """
        生成方法签名
        
        Args:
            method_name: 方法名
            template: 方法模板
            return_type: 返回类型
            
        Returns:
            方法签名字符串
        """
        signature_format = template.get("signature_format", "- (void){method_name};")
        
        # 替换占位符
        signature = signature_format.replace("{method_name}", method_name)
        signature = signature.replace("{return_type}", return_type)
        
        return signature
    
    def generate_method_body(self, template: Dict[str, Any], params: Optional[List[Dict]] = None,
                            return_type: str = "void", enable_code_blocks: bool = True) -> List[str]:
        """
        生成方法实现
        
        Args:
            template: 方法模板
            params: 参数列表
            return_type: 返回类型
            enable_code_blocks: 是否启用代码块多样性
            
        Returns:
            方法体行列表
        """
        body_template = template.get("body_template", [])
        body_lines = list(body_template)  # 复制模板
        
        # 获取方法中可用的变量名（从参数中）
        available_vars = set()
        if params:
            for param in params:
                param_name = param.get("name", "")
                if param_name:
                    available_vars.add(param_name)
        
        # 检查模板是否已经是完整的方法体（包含块语法或复杂结构）
        # 如果是，不添加额外的代码块
        is_complete_body = False
        body_str = '\n'.join(body_template)
        
        # 检查是否包含块语法 ^{ } 或复杂的嵌套结构
        if '^{' in body_str:
            is_complete_body = True
        # 检查是否包含 dispatch 调用（async/once）
        elif 'dispatch_async' in body_str or 'dispatch_once' in body_str:
            is_complete_body = True
        # 检查是否包含完整的循环或条件结构
        elif 'for (' in body_str and '}' in body_str:
            is_complete_body = True
        elif 'switch (' in body_str and '}' in body_str:
            is_complete_body = True
        # 检查是否包含 return 语句（错误处理方法等）
        elif 'return ' in body_str:
            is_complete_body = True
        # 检查是否包含 if 条件块
        elif 'if (' in body_str and '}' in body_str:
            is_complete_body = True
        # 简单模板（复杂度 1）不添加额外代码块
        elif template.get("complexity", 1) == 1:
            is_complete_body = True
        
        # 如果需要增加代码块多样性且模板不是完整的方法体
        if enable_code_blocks and not is_complete_body:
            # 随机插入额外的代码块
            block_type = self.random.choice(list(self.CODE_BLOCK_TEMPLATES.keys()))
            code_block = self.CODE_BLOCK_TEMPLATES[block_type]
            extra_line = self.random.choice(code_block)
            
            # 在方法体开始处插入日志或验证代码
            # 但只插入使用可用变量的代码块
            if block_type in ["log", "validation", "nullCheck"]:
                # 检查代码块是否只使用可用变量
                if self._code_block_uses_valid_vars(extra_line, available_vars):
                    # 处理多行代码块
                    for line in extra_line.split('\n'):
                        if line.strip():
                            body_lines.insert(1, line)
                            break  # 只插入第一行
            elif block_type in ["loop", "condition"]:
                # 对于循环和条件代码块，将多行拆分成单独的行
                for line in extra_line.split('\n'):
                    if line.strip():
                        body_lines.append(line)
        
        # 处理返回类型占位符
        default_value = self._get_default_value_for_type(return_type)
        body_lines = [line.replace("{default_value}", default_value) for line in body_lines]
        
        # 过滤掉使用未定义变量的行
        filtered_lines = []
        import re
        for line in body_lines:
            stripped = line.strip()
            # 跳过包含 return 语句且带有返回值的行（仅针对 void 返回类型）
            if return_type == "void" and stripped.startswith("return ") and stripped != "return;":
                # 检查是否是 instancetype 或 id 类型的返回
                if re.match(r'return\s+(instance|id|instanceType|nil|nullptr)\s*;', stripped, re.IGNORECASE):
                    # 保留 instancetype/nil 返回语句
                    pass
                elif re.match(r'return\s+\w+\s*;', stripped):
                    # 这是普通变量返回，跳过
                    continue
                else:
                    # 其他 return 语句，跳过
                    continue
            # 处理条件语句中的 return（如 if (condition) { return X; }）
            if return_type == "void" and re.search(r'\breturn\s+\w+\s*;', stripped):
                if stripped.startswith("if ") or stripped.startswith("if("):
                    # 保留 if 条件但移除 return 部分
                    # 简单处理：跳过这行
                    continue
            # 跳过使用未定义变量的行（但保留注释和 return 语句）
            if not stripped.startswith("return ") and not stripped.startswith("//"):
                if not self._code_block_uses_valid_vars(line, available_vars):
                    # 替换为安全的注释或空行
                    if "//" not in line:
                        continue
            filtered_lines.append(line)
        body_lines = filtered_lines
        
        return body_lines
    
    def _code_block_uses_valid_vars(self, code_line: str, available_vars: set) -> bool:
        """
        检查代码行是否只使用可用的变量
        
        Args:
            code_line: 代码行
            available_vars: 可用变量名集合
            
        Returns:
            如果代码行只使用可用变量或没有使用变量则返回 True
        """
        import re
        
        # 如果没有任何可用变量，只允许不包含变量引用的代码
        if not available_vars:
            # 检查是否包含常见的变量引用模式
            var_pattern = r'\b(array|block|key|value|object|result|param|param\d+)\b'
            matches = re.findall(var_pattern, code_line)
            return len(matches) == 0
        
        # 提取代码行中使用的变量名
        var_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b'
        matches = re.findall(var_pattern, code_line)
        
        # 过滤掉 Objective-C 关键字和方法名
        objc_keywords = {
            'if', 'else', 'for', 'in', 'while', 'do', 'switch', 'case', 'default',
            'return', 'break', 'continue', 'goto', 'sizeof', 'typeof',
            'self', 'super', 'nil', 'Nil', 'NULL', 'YES', 'NO',
            'id', 'Class', 'SEL', 'IMP', 'BOOL', 'instancetype',
            'NSString', 'NSArray', 'NSDictionary', 'NSSet', 'NSMutableArray',
            'NSMutableDictionary', 'NSMutableSet', 'NSNumber', 'NSDate',
            'NSLog', 'NSAssert', 'NSParameterAssert',
            'dispatch_async', 'dispatch_get_global_queue', 'dispatch_get_main_queue',
            'dispatch_once', 'dispatch_once_t',
            'autorelease', 'retain', 'release', 'copy', 'mutableCopy',
            'alloc', 'init', 'new', 'dealloc',
            'respondsToSelector', 'performSelector', 'isKindOfClass',
            'stringWithFormat', 'arrayWithCapacity', 'dictionaryWithCapacity',
            'setObject', 'objectForKey', 'addObject', 'removeObject',
            'count', 'length', 'isEmpty', 'description',
            'class', 'selector', 'method', 'encode',
            'true', 'false', 'nullptr', 'void', 'int', 'float', 'double',
            'char', 'short', 'long', 'unsigned', 'signed', 'const', 'static',
            'extern', 'register', 'volatile', 'inline', 'virtual', 'explicit',
            'friend', 'typedef', 'enum', 'struct', 'union', 'namespace',
            'using', 'template', 'typename', 'class', 'public', 'private', 'protected',
            'try', 'catch', 'throw', 'new', 'delete', 'this',
            'OS_LOG_DEFAULT', 'os_log', 'NSLocalizedDescriptionKey',
            'NSError', 'errorWithDomain', 'code', 'userInfo',
            'NSMutableArray', 'arrayWithCapacity', 'NSSet', 'set',
            'NSDateFormatter', 'localizedStringFromDate', 'dateStyle', 'timeStyle',
            'NSDate', 'NSDateFormatterMediumStyle',
            'NSStringFromClass', 'NSStringFromSelector',
            'func', 'cmd', 'self', 'cache', 'fetchValueForKey',
            'processObject', 'validate', 'processResult', 'writeLog',
            'currentValue', '_currentValue',
            'i', 'idx', 'stop', 'obj', 'item', 'obj', 'count', 'maxCount',
            'condition', 'state', 'StateA', 'StateB', 'StateC',
            'type', 'TypeA', 'TypeB', 'TypeC', 'Unknown',
            'message', 'timestamp', 'logMessage',
            'identifier', 'cached', 'object',
            'array', 'block', 'key', 'value', 'result', 'param', 'error',
            'completion', 'callback', 'success',
            'onceToken', 'sharedInstance', 'instance',
            'queue', 'operation', 'main', 'global',
            'OS_LOG_DEFAULT', 'public',
            'typeid', 'typename', 'begin', 'end',
            'OSLogType', 'OSLog',
            'enumerateObjectsUsingBlock'
        }
        
        for match in matches:
            if match not in available_vars and match not in objc_keywords:
                # 检查是否是指针类型声明的一部分
                if match in ['NSString', 'NSArray', 'NSDictionary', 'NSSet', 'id', 'NSObject', 'NSError', 'NSDate', 'NSNumber', 'NSCache', 'NSOperationQueue', 'NSDateFormatter', 'NSMutableArray', 'NSMutableDictionary']:
                    continue
                # 这是一个未定义的变量
                return False
        
        return True
    
    def _get_default_value_for_type(self, return_type: str) -> str:
        """
        获取类型的默认值
        
        Args:
            return_type: 返回类型
            
        Returns:
            默认值字符串
        """
        if return_type in ["void"]:
            return ""
        elif return_type in ["int", "NSInteger", "NSUInteger", "long", "short"]:
            return "0"
        elif return_type in ["float", "double", "CGFloat"]:
            return "0.0f"
        elif return_type in ["BOOL", "bool"]:
            return "YES"
        elif return_type in ["NSString *"]:
            return "@\"\""
        elif return_type in ["NSArray *", "NSMutableArray *"]:
            return "@[]"
        elif return_type in ["NSDictionary *", "NSMutableDictionary *"]:
            return "@{}"
        elif return_type in ["NSSet *"]:
            return "[NSSet set]"
        elif return_type in ["id", "instancetype"]:
            return "nil"
        elif return_type.endswith(" *"):
            return "nil"
        else:
            return "nil"
    
    def get_code_block(self, block_type: str) -> str:
        """
        获取指定类型的代码块 (Objective-C)
        
        Args:
            block_type: 代码块类型 (log/validation/nullCheck/errorHandling/async/cache/loop/condition)
            
        Returns:
            代码块字符串
        """
        if block_type in self.CODE_BLOCK_TEMPLATES:
            return self.random.choice(self.CODE_BLOCK_TEMPLATES[block_type])
        return "// Unknown code block type"
    
    def generate_cpp_code_block(self, block_type: str) -> str:
        """
        获取指定类型的 C++ 代码块
        
        Args:
            block_type: 代码块类型 (log/validation/nullCheck/errorHandling/async/cache/loop/condition/singleton/factory)
            
        Returns:
            C++ 代码块字符串
        """
        if block_type in self.CPP_CODE_BLOCK_TEMPLATES:
            return self.random.choice(self.CPP_CODE_BLOCK_TEMPLATES[block_type])
        return "// Unknown C++ code block type"
    
    def get_cpp_type(self, objc_type: str) -> str:
        """
        将 Objective-C 类型转换为 C++ 类型
        
        Args:
            objc_type: Objective-C 类型
            
        Returns:
            C++ 类型字符串
        """
        return self.CPP_TYPE_MAPPING.get(objc_type, objc_type)
    
    def generate_cpp_method_signature(self, method_name: str, template: Dict[str, Any],
                                       class_name: str = "", return_type: str = "void") -> str:
        """
        生成 C++ 方法签名
        
        Args:
            method_name: 方法名
            template: 方法模板
            class_name: 类名（用于单例/工厂方法）
            return_type: 返回类型
            
        Returns:
            C++ 方法签名字符串
        """
        signature_format = template.get("signature_format", "void {method_name}()")
        
        # 替换占位符
        signature = signature_format.replace("{method_name}", method_name)
        signature = signature.replace("{return_type}", return_type)
        signature = signature.replace("{class_name}", class_name)
        
        return signature
    
    def generate_cpp_method_body(self, template: Dict[str, Any], params: Optional[List[Dict]] = None,
                                  return_type: str = "void", class_name: str = "",
                                  enable_code_blocks: bool = True) -> List[str]:
        """
        生成 C++ 方法实现
        
        Args:
            template: 方法模板
            params: 参数列表
            return_type: 返回类型
            class_name: 类名
            enable_code_blocks: 是否启用代码块多样性
            
        Returns:
            C++ 方法体行列表
        """
        body_template = template.get("body_template", [])
        body_lines = list(body_template)  # 复制模板
        
        # 处理类名占位符
        body_lines = [line.replace("{class_name}", class_name) for line in body_lines]
        
        # 如果需要增加代码块多样性
        if enable_code_blocks:
            # 随机插入额外的 C++ 代码块
            block_type = self.random.choice(list(self.CPP_CODE_BLOCK_TEMPLATES.keys()))
            code_block = self.CPP_CODE_BLOCK_TEMPLATES[block_type]
            extra_line = self.random.choice(code_block)
            
            # 在方法体开始处插入日志或验证代码
            if block_type in ["log", "validation", "nullCheck"]:
                body_lines.insert(1, extra_line)
        
        # 处理返回类型占位符
        default_value = self._get_cpp_default_value_for_type(return_type)
        body_lines = [line.replace("{default_value}", default_value) for line in body_lines]
        
        return body_lines
    
    def _get_cpp_default_value_for_type(self, return_type: str) -> str:
        """
        获取 C++ 类型的默认值
        
        Args:
            return_type: 返回类型
            
        Returns:
            默认值字符串
        """
        if return_type in ["void"]:
            return ""
        elif return_type in ["int", "long", "short", "size_t", "NSInteger", "NSUInteger"]:
            return "0"
        elif return_type in ["float", "double", "CGFloat"]:
            return "0.0f"
        elif return_type in ["BOOL", "bool"]:
            return "false"
        elif return_type in ["std::string"]:
            return '""'
        elif return_type in ["NSArray *", "NSMutableArray *", "std::vector<void*>"]:
            return "{}"
        elif return_type in ["NSDictionary *", "NSMutableDictionary *", "std::map<std::string, void*>"]:
            return "{}"
        elif return_type in ["id", "instancetype", "void*", "ClassName*"]:
            return "nullptr"
        elif return_type.endswith("*"):
            return "nullptr"
        else:
            return "{}"
    
    def select_cpp_method_template(self, class_type: str, method_index: int = 0,
                                    diversity_level: str = "high") -> Dict[str, Any]:
        """
        根据类类型选择 C++ 模板
        
        Args:
            class_type: 类类型
            method_index: 方法索引
            diversity_level: 多样性级别 (low/medium/high)
            
        Returns:
            选中的方法模板
        """
        # 获取适用于该类类型的 C++ 模板
        applicable_templates = []
        for template_name, template in self.CPP_METHOD_TEMPLATES.items():
            if class_type in template.get("applicable_types", []):
                applicable_templates.append((template_name, template))
        
        if not applicable_templates:
            # 如果没有适用的模板，返回默认模板
            return self.CPP_METHOD_TEMPLATES["simple_void"]
        
        # 根据多样性级别选择模板
        if diversity_level == "low":
            # 低多样性：优先选择简单模板
            simple_templates = [(n, t) for n, t in applicable_templates if t.get("complexity", 1) <= 2]
            if simple_templates:
                return self.random.choice(simple_templates)[1]
            return self.random.choice(applicable_templates)[1]
        
        elif diversity_level == "medium":
            # 中等多样性：按复杂度加权选择
            weights = [max(1, 4 - t.get("complexity", 1)) for _, t in applicable_templates]
            return self.random.choices(applicable_templates, weights=weights)[0][1]
        
        else:  # high
            # 高多样性：完全随机选择
            return self.random.choice(applicable_templates)[1]
    
    def generate_class_type_methods(self, class_name: str, method_count: int,
                                   diversity_config: Optional[Dict[str, bool]] = None) -> List[Dict[str, Any]]:
        """
        根据类类型生成多个方法
        
        Args:
            class_name: 类名
            method_count: 方法数量
            diversity_config: 多样性配置
            
        Returns:
            方法信息列表
        """
        class_type = self.detect_class_type(class_name)
        methods = []
        
        # 默认多样性配置
        if diversity_config is None:
            diversity_config = {
                "enableAsyncMethods": True,
                "enableBlockCallbacks": True,
                "enableErrorHandling": True,
                "enableChainableMethods": True,
                "enableFactoryMethods": True,
                "enableSingletonPattern": True,
                "enableCacheLogic": True,
                "enableValidationLogic": True,
                "enableLoggingLogic": True
            }
        
        # 获取类类型对应的特殊方法
        special_methods = self._get_special_methods_for_class_type(class_type, diversity_config)
        
        for i in range(method_count):
            # 选择模板
            template = self.select_method_template(class_type, i, "high")
            
            # 生成方法名
            method_name = self._generate_method_name_for_template(template, i)
            
            # 生成方法信息
            method_info = {
                "name": method_name,
                "template": template,
                "class_type": class_type,
                "complexity": template.get("complexity", 1)
            }
            
            methods.append(method_info)
        
        return methods
    
    def _get_special_methods_for_class_type(self, class_type: str, config: Dict[str, bool]) -> List[str]:
        """
        获取类类型对应的特殊方法
        
        Args:
            class_type: 类类型
            config: 多样性配置
            
        Returns:
            特殊方法名列表
        """
        special_methods = []
        
        if class_type == "manager" and config.get("enableSingletonPattern", True):
            special_methods.append("sharedInstance")
        
        if class_type == "factory" and config.get("enableFactoryMethods", True):
            special_methods.append("createInstance")
        
        if class_type == "storage" and config.get("enableCacheLogic", True):
            special_methods.append("cachedObjectForKey")
        
        return special_methods
    
    def _generate_method_name_for_template(self, template: Dict[str, Any], index: int) -> str:
        """
        为模板生成方法名
        
        Args:
            template: 方法模板
            index: 方法索引
            
        Returns:
            方法名
        """
        # 检查模板是否有固定的方法名（从 signature_format 中提取）
        signature_format = template.get("signature_format", "")
        
        # 对于包含固定方法名的模板，直接提取方法名
        # 例如："+ (instancetype)sharedInstance;" 应返回 "sharedInstance"
        # 例如："- (id)createInstance;" 应返回 "createInstance"
        import re
        
        # 匹配 Objective-C 类方法：+ (returnType)methodName
        class_method_match = re.search(r'\+\s*\([^)]+\)\s*(\w+)', signature_format)
        if class_method_match:
            return class_method_match.group(1)
        
        # 匹配 Objective-C 实例方法：- (returnType)methodName
        instance_method_match = re.search(r'-\s*\([^)]+\)\s*(\w+)', signature_format)
        if instance_method_match:
            method_name = instance_method_match.group(1)
            # 检查是否包含参数（方法名后是否有冒号）
            if ':' in signature_format:
                # 对于带参数的方法，提取第一个参数前的部分作为方法名主体
                method_name = method_name.split(':')[0]
            return method_name
        
        # 对于没有固定方法名的模板，使用通用命名规则
        # 方法名前缀
        prefixes = ["perform", "execute", "handle", "process", "run", "start", "begin", "init"]
        prefix = self.random.choice(prefixes)
        
        # 方法名主体
        subjects = ["Operation", "Task", "Request", "Command", "Action", "Work", "Job", "Procedure"]
        subject = self.random.choice(subjects)
        
        return f"{prefix}{subject}{index}"
