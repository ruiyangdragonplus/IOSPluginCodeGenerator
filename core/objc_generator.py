"""
Objective-C 代码生成器模块
负责生成 .h 头文件和 .m 实现文件
"""

from typing import Dict, List, Any, Optional


class ObjCGenerator:
    """Objective-C 代码生成器类"""
    
    def __init__(self, class_prefix: str = ""):
        """
        初始化 Objective-C 生成器
        
        Args:
            class_prefix: 类名前缀
        """
        self.class_prefix = class_prefix
    
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
            for method in methods:
                method_decl = self._generate_method_declaration(method)
                lines.append(method_decl)
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
        
        # 构建方法签名
        if not params:
            method_sig = method_name
        else:
            parts = [method_name]
            for i, param in enumerate(params):
                param_name = param.get("name", f"param{i}")
                param_type = param.get("type", "id")
                if i == 0:
                    parts.append(f"{param_name}:({param_type}){param_name}")
                else:
                    parts.append(f" {param_name}:({param_type}){param_name}")
            method_sig = "".join(parts)
        
        # 生成方法体
        lines = []
        if not params:
            if return_type == "void":
                lines.append(f"- (void){method_sig} {{")
            else:
                lines.append(f"- ({return_type}){method_sig} {{")
        else:
            if return_type == "void":
                lines.append(f"- (void){method_sig} {{")
            else:
                lines.append(f"- ({return_type}){method_sig} {{")
        
        # 根据复杂度生成方法体内容
        body_lines = self._generate_method_body(complexity, params, return_type)
        for body_line in body_lines:
            lines.append(f"    {body_line}")
        
        # 返回值
        if return_type != "void":
            if return_type in ["int", "NSInteger"]:
                lines.append("    return 0;")
            elif return_type in ["float", "double", "CGFloat"]:
                lines.append("    return 0.0f;")
            elif return_type == "BOOL":
                lines.append("    return YES;")
            elif return_type == "NSString *":
                lines.append('    return @"";')
            elif return_type == "NSArray *":
                lines.append("    return @[];")
            elif return_type == "NSDictionary *":
                lines.append("    return @{};")
            else:
                lines.append("    return nil;")
        
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
            lines.append("NSLog(@\"%s called\", __func__);")
        
        elif complexity == 2:
            # 中等方法
            lines.append("// Medium complexity implementation")
            lines.append("NSLog(@\"%s called\", __func__);")
            lines.append("")
            lines.append("if (self) {")
            lines.append("    // Process request")
            lines.append("}")
        
        elif complexity >= 3:
            # 复杂方法
            lines.append("// Complex implementation")
            lines.append("NSLog(@\"%s called\", __func__);")
            lines.append("")
            lines.append("for (int i = 0; i < 10; i++) {")
            lines.append("    // Process item")
            lines.append("    if (i % 2 == 0) {")
            lines.append("        NSLog(@\"Processing even index: %d\", i);")
            lines.append("    }")
            lines.append("}")
        
        return lines
    
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
