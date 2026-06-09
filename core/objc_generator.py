"""
Objective-C 代码生成器模块
负责生成 .h 头文件和 .m 实现文件
"""

from typing import Dict, List, Any, Optional
from .template_engine import TemplateEngine


class ObjCGenerator:
    """Objective-C 代码生成器类"""
    
    def __init__(self, class_prefix: str = "", vocabulary: Optional[Dict[str, Any]] = None,
                 diversity_config: Optional[Dict[str, Any]] = None):
        """
        初始化 Objective-C 生成器
        
        Args:
            class_prefix: 类名前缀
            vocabulary: 词库配置
            diversity_config: 多样性配置
        """
        self.class_prefix = class_prefix
        self.template_engine = TemplateEngine(vocabulary)
        self.diversity_config = diversity_config or {
            "diversityLevel": "high",
            "enableAsyncMethods": True,
            "enableBlockCallbacks": True,
            "enableErrorHandling": True,
            "enableGenericTypes": True,
            "enableChainableMethods": True,
            "enableFactoryMethods": True,
            "enableSingletonPattern": True,
            "enableDelegatePattern": True,
            "enableCacheLogic": True,
            "enableValidationLogic": True,
            "enableLoggingLogic": True
        }
    
    def set_seed(self, seed: int):
        """设置随机种子"""
        self.template_engine.set_seed(seed)
    
    def _extract_return_type_from_signature(self, signature_format: str) -> str:
        """
        从方法签名格式中提取返回类型
        
        Args:
            signature_format: 方法签名格式字符串
            
        Returns:
            返回类型字符串，如果无法提取则返回空字符串
        """
        import re
        
        # 匹配 Objective-C 类方法：+ (returnType)methodName
        # 使用 [^\s;]+ 而不是 \w+ 来匹配包含占位符的方法名（如 {method_name}）
        class_method_match = re.search(r'\+\s*\(([^)]+)\)\s*([^\s;]+)', signature_format)
        if class_method_match:
            return class_method_match.group(1).strip()
        
        # 匹配 Objective-C 实例方法：- (returnType)methodName
        instance_method_match = re.search(r'-\s*\(([^)]+)\)\s*([^\s;]+)', signature_format)
        if instance_method_match:
            return instance_method_match.group(1).strip()
        
        return ""
    
    def generate_header(
        self,
        class_name: str,
        parent_class: str = "NSObject",
        properties: Optional[List[Dict[str, str]]] = None,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        生成 Objective-C 头文件内容
        
        Args:
            class_name: 类名
            parent_class: 父类名
            properties: 属性列表，每个元素包含 name 和 type
            methods: 方法列表，每个元素包含 name, return_type, params
            
        Returns:
            头文件内容
        """
        lines = []
        
        # 导入语句
        lines.append("#import <Foundation/Foundation.h>")
        lines.append("")
        
        # 类声明
        lines.append(f"@interface {class_name} : {parent_class}")
        lines.append("")
        
        # 属性声明
        if properties:
            for prop in properties:
                prop_name = prop.get("name", "")
                prop_type = prop.get("type", "id")
                attributes = self._get_property_attributes(prop_type)
                lines.append(f"@property (nonatomic, {attributes}) {prop_type} {prop_name};")
            lines.append("")
        
        # 方法声明
        if methods:
            used_method_names = set()  # 跟踪已使用的方法名，避免重复声明
            for method in methods:
                # 生成方法签名用于检查唯一性
                method_signature = self._generate_method_declaration(method)
                # 提取方法名进行唯一性检查
                method_name = method.get("name", "")
                if method_name in used_method_names:
                    continue  # 跳过重复的方法名
                used_method_names.add(method_name)
                lines.append(method_signature)
            lines.append("")
        
        lines.append("@end")
        
        return "\n".join(lines)
    
    def _get_property_attributes(self, prop_type: str) -> str:
        """
        根据类型获取属性属性
        
        Args:
            prop_type: 属性类型
            
        Returns:
            属性属性字符串
        """
        # 基本类型使用 assign
        basic_types = ["int", "float", "double", "BOOL", "NSInteger", "NSUInteger", "CGFloat"]
        if prop_type in basic_types:
            return "assign"
        # 对象类型使用 strong
        return "strong"
    
    def _generate_method_declaration(self, method: Dict[str, Any]) -> str:
        """
        生成方法声明
        
        Args:
            method: 方法信息
            
        Returns:
            方法声明字符串
        """
        # 如果方法包含模板，使用模板引擎生成签名
        if "template" in method:
            template = method["template"]
            method_name = method.get("name", "")
            return_type = method.get("return_type", "void")
            return self.template_engine.generate_method_signature(method_name, template, return_type)
        
        # 否则使用传统方式生成
        method_name = method.get("name", "")
        return_type = method.get("return_type", "void")
        params = method.get("params", [])
        
        if not params:
            # 无参数方法
            if return_type == "void":
                return f"- (void){method_name};"
            else:
                return f"- ({return_type}){method_name};"
        else:
            # 有参数方法
            # 方法名格式：methodNameWithParam1:param1 param2:param2 ...
            parts = [method_name]
            for i, param in enumerate(params):
                param_name = param.get("name", f"param{i}")
                param_type = param.get("type", "id")
                if i == 0:
                    parts.append(f"{param_name}:({param_type}){param_name}")
                else:
                    parts.append(f" {param_name}:({param_type}){param_name}")
            
            method_sig = "".join(parts)
            if return_type == "void":
                return f"- (void){method_sig};"
            else:
                return f"- ({return_type}){method_sig};"
    
    def generate_implementation(
        self,
        class_name: str,
        properties: Optional[List[Dict[str, str]]] = None,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        生成 Objective-C 实现文件内容
        
        Args:
            class_name: 类名
            properties: 属性列表
            methods: 方法列表
            
        Returns:
            实现文件内容
        """
        lines = []
        
        # 导入头文件
        lines.append(f'#import "{class_name}.h"')
        lines.append("")
        
        # 类扩展（私有属性）
        lines.append(f"@interface {class_name} ()")
        lines.append("")
        # 添加常用的私有属性声明，避免未定义变量错误
        lines.append("@property (nonatomic, weak) id delegate;")
        lines.append("@property (nonatomic, strong) NSCache *cache;")
        lines.append("@end")
        lines.append("")
        
        # 实现开始
        lines.append(f"@implementation {class_name}")
        lines.append("")
        
        # 合成属性
        if properties:
            lines.append("#pragma mark - Properties")
            lines.append("")
            for prop in properties:
                prop_name = prop.get("name", "")
                lines.append(f"@synthesize {prop_name} = _{prop_name};")
            lines.append("")
        
        # 方法实现
        if methods:
            lines.append("#pragma mark - Methods")
            lines.append("")
            for method in methods:
                method_impl = self._generate_method_implementation(class_name, method)
                lines.append(method_impl)
                lines.append("")
        
        lines.append("@end")
        
        return "\n".join(lines)
    
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
        
        # 使用与头文件相同的方法生成方法签名
        method_sig = self._generate_method_signature_for_implementation(method)

        # 真实声明的返回类型：从签名里提取（而非可能被 override 的 return_type 字段），
        # 保证兜底 return 与签名一致，避免「void 方法却 return 值」
        decl_return = self._extract_return_type_from_signature(method_sig) or "void"
        
        # 生成方法体
        lines = []
        
        # 如果方法包含模板，使用模板引擎生成方法体
        is_complete_template = False
        has_return_statement = False
        if "template" in method:
            template = method["template"]
            template_params = self._extract_params_from_template(template)
            if template_params:
                params = template_params
            
            enable_code_blocks = self.diversity_config.get("diversityLevel", "high") == "high"
            body_lines = self.template_engine.generate_method_body(
                template, params, return_type, enable_code_blocks
            )
            # 检查生成的 body_lines 是否包含 return 语句
            # 注意：使用生成的 body_lines 而不是原始模板，因为 generate_method_body 可能过滤掉某些行
            body_str = '\n'.join(body_lines)
            # 检查是否包含 return 语句
            if 'return ' in body_str:
                has_return_statement = True
            # 检查是否包含块语法（dispatch_async/dispatch_once）
            has_block_syntax = '^{' in body_str or 'dispatch_async' in body_str or 'dispatch_once' in body_str
            # 检查是否包含循环结构（for in 循环）
            has_loop_syntax = 'for (' in body_str or 'for id ' in body_str
            # 检查是否包含条件结构
            has_condition_syntax = 'if (' in body_str
            
            # 包含 return 语句的模板是完整模板（无论是否有块语法）
            if has_return_statement:
                is_complete_template = True
            # 包含块语法的模板也是完整模板（如 async 方法不需要额外 return）
            elif has_block_syntax:
                is_complete_template = True
            # 包含循环或条件结构的模板也是完整模板
            elif has_loop_syntax or has_condition_syntax:
                is_complete_template = True
        else:
            body_lines = self._generate_method_body(complexity, params, return_type)
        
        # 添加方法签名（从 method_sig 提取）
        lines.append(f"{method_sig} {{")
        
        # 处理多行模板（将每个 body_line 按换行符拆分）
        # 根据代码块的嵌套层次动态调整缩进
        # 使用缩进栈来跟踪嵌套层次
        indent_stack = [1]  # 方法体内的基础缩进层次为 1
        
        for body_line in body_lines:
            for line in body_line.split('\n'):
                stripped = line.strip()
                if not stripped:
                    lines.append("")
                    continue
                
                # 检查是否是块结束标记（}); 或 }）
                # 这些应该先减少缩进再输出
                if stripped.startswith('}'):
                    if len(indent_stack) > 1:
                        indent_stack.pop()
                
                # 添加当前行
                current_indent = indent_stack[-1]
                lines.append("    " * current_indent + stripped)
                
                # 如果行以 { 结尾（不包括字符串字面量中的 {），增加缩进层次
                # 注意：^{ 是块语法的一部分，需要增加缩进
                if stripped.endswith('{'):
                    indent_stack.append(current_indent + 1)
        
        # 返回值 - 仅当（签名声明的）返回类型不是 void 时添加
        # 但如果模板已经是完整的方法体（包含 return），不添加
        if decl_return != "void" and not is_complete_template:
            if decl_return in ["int", "NSInteger", "NSUInteger"]:
                lines.append("    return 0;")
            elif decl_return in ["float", "double", "CGFloat"]:
                lines.append("    return 0.0f;")
            elif decl_return == "BOOL":
                lines.append("    return YES;")
            elif "NSString" in decl_return:
                lines.append('    return @"";')
            elif decl_return.startswith("NSArray"):
                lines.append("    return @[];")
            elif decl_return.startswith("NSDictionary"):
                lines.append("    return @{};")
            else:
                lines.append("    return nil;")
        
        # 添加方法结束符 - 所有方法都需要 } 来闭合
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_method_signature_for_implementation(self, method: Dict[str, Any]) -> str:
        """
        生成实现文件中的方法签名（与头文件保持一致）
        
        Args:
            method: 方法信息
            
        Returns:
            方法签名字符串（不带分号和末尾的 {）
        """
        method_name = method.get("name", "")
        return_type = method.get("return_type", "void")
        
        # 如果方法包含模板，使用模板引擎生成签名
        if "template" in method:
            template = method["template"]
            signature = self.template_engine.generate_method_signature(method_name, template, return_type)
            # 移除分号
            signature = signature.rstrip(';')
            return signature
        
        # 否则使用传统方式生成
        params = method.get("params", [])
        
        if not params:
            # 无参数方法
            if return_type == "void":
                return f"- (void){method_name}"
            else:
                return f"- ({return_type}){method_name}"
        else:
            # 有参数方法
            parts = [method_name]
            for i, param in enumerate(params):
                param_name = param.get("name", f"param{i}")
                param_type = param.get("type", "id")
                if i == 0:
                    parts.append(f"{param_name}:({param_type}){param_name}")
                else:
                    parts.append(f" {param_name}:({param_type}){param_name}")
            
            method_sig = "".join(parts)
            if return_type == "void":
                return f"- (void){method_sig}"
            else:
                return f"- ({return_type}){method_sig}"
    
    def _extract_params_from_template(self, template: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        从模板签名格式中提取参数列表
        
        Args:
            template: 方法模板
            
        Returns:
            参数列表，每个元素包含 name 和 type
        """
        signature_format = template.get("signature_format", "")
        params = []
        
        # 解析签名格式中的参数
        # 格式示例："- (void){method_name}WithArray:(NSArray *)array;"
        # 或："- (void){method_name}WithBlock:(void (^)(id result))block;"
        
        # 查找所有 :(Type)name 模式
        import re
        # 匹配 :(type)name 模式，包括复杂的 block 类型
        pattern = r':\s*\(([^)]+(?:\)[^)]*)*)\)\s*(\w+)'
        matches = re.findall(pattern, signature_format)
        
        for match in matches:
            param_type = match[0].strip()
            param_name = match[1].strip()
            # 移除类型中的占位符
            param_type = param_type.replace("{return_type}", "id")
            params.append({
                "name": param_name,
                "type": param_type
            })
        
        return params
    
    def _generate_method_body(self, complexity: int, params: List[Dict], return_type: str) -> List[str]:
        """
        根据复杂度生成方法体内容（传统方式）
        
        Args:
            complexity: 复杂度等级
            params: 参数列表
            return_type: 返回类型
            
        Returns:
            方法体行列表
        """
        lines = []
        
        # 从词库中获取代码块模板
        builtin = self.template_engine.vocabulary.get("builtin", {}) if self.template_engine.vocabulary else {}
        code_blocks = builtin.get("codeBlock", {})
        
        if complexity == 1:
            # 简单方法
            lines.append("// Simple implementation")
            if code_blocks.get("log"):
                lines.append(self.template_engine.random.choice(code_blocks["log"]))
            else:
                lines.append("NSLog(@\"%s called\", __func__);")
        
        elif complexity == 2:
            # 中等方法
            lines.append("// Medium complexity implementation")
            if code_blocks.get("log"):
                lines.append(self.template_engine.random.choice(code_blocks["log"]))
            lines.append("")
            if code_blocks.get("validation"):
                lines.append(self.template_engine.random.choice(code_blocks["validation"]))
            else:
                lines.append("if (self) {")
                lines.append("    // Process request")
                lines.append("}")
        
        elif complexity >= 3:
            # 复杂方法
            lines.append("// Complex implementation")
            if code_blocks.get("log"):
                lines.append(self.template_engine.random.choice(code_blocks["log"]))
            lines.append("")
            if code_blocks.get("loop"):
                loop_block = self.template_engine.random.choice(code_blocks["loop"])
                # 将多行模板拆分成单独的行并添加适当的缩进
                for loop_line in loop_block.split('\n'):
                    if loop_line.strip():
                        lines.append("    " + loop_line.strip())
        
        return lines
    
    def generate_method_with_template(self, class_name: str, method_index: int = 0) -> Dict[str, Any]:
        """
        使用模板引擎生成方法
        
        Args:
            class_name: 类名
            method_index: 方法索引
            
        Returns:
            方法信息字典
        """
        class_type = self.template_engine.detect_class_type(class_name)
        template = self.template_engine.select_method_template(
            class_type, method_index, 
            self.diversity_config.get("diversityLevel", "high")
        )
        
        # 生成方法名
        method_name = self.template_engine._generate_method_name_for_template(template, method_index)
        
        # 从模板的 signature_format 中提取返回类型
        signature_format = template.get("signature_format", "")
        return_type = self._extract_return_type_from_signature(signature_format)

        # 如果无法提取、或提取到的是占位符（如 {return_type}），则选一个具体类型
        if not return_type or "{" in return_type:
            concrete_types = ["NSInteger", "BOOL", "NSString *", "id", "NSArray *", "NSDictionary *"]
            return_type = self.template_engine.random.choice(concrete_types)
        
        return {
            "name": method_name,
            "return_type": return_type,
            "template": template,
            "class_type": class_type,
            "complexity": template.get("complexity", 1),
            "params": []
        }
    
    def generate_files(
        self,
        class_name: str,
        properties: Optional[List[Dict[str, str]]] = None,
        methods: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, str]]:
        """
        生成完整的类文件（头文件和实现文件）
        
        Args:
            class_name: 类名
            properties: 属性列表
            methods: 方法列表
            
        Returns:
            文件列表，包含 filename 和 content
        """
        header_content = self.generate_header(class_name, properties=properties, methods=methods)
        impl_content = self.generate_implementation(class_name, properties=properties, methods=methods)
        
        return [
            {"filename": f"{class_name}.h", "content": header_content},
            {"filename": f"{class_name}.m", "content": impl_content}
        ]
