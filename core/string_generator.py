"""
String 常量生成器模块
负责生成包含多个 String 常量的 .m 或 .cpp 文件
"""

import random
from typing import List, Dict, Any, Optional


class StringGenerator:
    """String 常量生成器类"""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        """
        初始化 String 生成器
        
        Args:
            vocabulary: 词库配置
        """
        self.vocabulary = vocabulary or {}
        self.random = random.Random()
    
    def set_seed(self, seed: int):
        """
        设置随机种子
        
        Args:
            seed: 随机种子
        """
        self.random.seed(seed)
    
    def generate_random_content(self, mode: str = "word") -> str:
        """
        从词库随机组合生成内容
        
        Args:
            mode: 生成模式，"word" 为词汇，"sentence" 为句子
            
        Returns:
            生成的 String 内容
        """
        class_vocab = self.vocabulary.get("class", {})
        prefixes = class_vocab.get("prefix", [])
        middles = class_vocab.get("middle", [])
        suffixes = class_vocab.get("suffixNoun", [])
        
        if mode == "sentence":
            # 生成句子模式：2-4 个词组合
            parts_count = self.random.randint(2, 4)
            parts = []
            
            for _ in range(parts_count):
                source = self.random.choice([prefixes, middles, suffixes])
                if source:
                    parts.append(self.random.choice(source))
            
            return " ".join(parts) if parts else "Default String Value"
        else:
            # 生成词汇模式：1-2 个词组合
            parts_count = self.random.randint(1, 2)
            parts = []
            
            if parts_count >= 1 and prefixes:
                parts.append(self.random.choice(prefixes))
            if parts_count >= 2 and middles:
                parts.append(self.random.choice(middles))
            
            return " ".join(parts) if parts else "Default String Value"
    
    def generate_string_constant(self, index: int, mode: str = "word") -> Dict[str, str]:
        """
        生成单个 String 常量
        
        Args:
            index: 常量索引
            mode: 生成模式，"word" 或 "sentence"
            
        Returns:
            包含 constant_name 和 content 的字典
        """
        content = self.generate_random_content(mode)
        return {
            "constant_name": f"ABStringConstant_{index}",
            "content": content
        }
    
    def generate_objc_file(self, string_count: int, mode: str = "word") -> str:
        """
        生成 Objective-C 格式的 String 常量文件
        
        Args:
            string_count: String 数量
            mode: 生成模式
            
        Returns:
            文件内容
        """
        lines = []
        
        # 文件头注释
        lines.append("// ABStringConstants.m")
        lines.append("#import <Foundation/Foundation.h>")
        lines.append("")
        
        # 生成常量声明
        for i in range(string_count):
            string_data = self.generate_string_constant(i, mode)
            lines.append(f'static NSString * const {string_data["constant_name"]} = @"{string_data["content"]}";')
        
        lines.append("")
        
        # 生成打印函数
        lines.append("void ABPrintStringConstants() {")
        lines.append("    if (YES) return;")
        
        for i in range(string_count):
            lines.append(f'    NSLog(@"%@", ABStringConstant_{i});')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_cpp_file(self, string_count: int, mode: str = "word") -> str:
        """
        生成 C++ 格式的 String 常量文件
        
        Args:
            string_count: String 数量
            mode: 生成模式
            
        Returns:
            文件内容
        """
        lines = []
        
        # 文件头注释
        lines.append("// ABStringConstants.cpp")
        lines.append("#include <cstdio>")
        lines.append("")
        
        # 生成常量声明
        for i in range(string_count):
            string_data = self.generate_string_constant(i, mode)
            lines.append(f'static const char {string_data["constant_name"]}[] = "{string_data["content"]}";')
        
        lines.append("")
        
        # 生成打印函数
        lines.append("void ABPrintStringConstants() {")
        lines.append("    if (true) return;")
        
        for i in range(string_count):
            lines.append(f'    printf("%s\\n", ABStringConstant_{i});')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_file(self, string_count: int, language: str = "objc", mode: str = "word") -> Dict[str, str]:
        """
        生成完整的 String 常量文件
        
        Args:
            string_count: String 数量
            language: 语言选项，"objc" 或 "cpp"
            mode: 生成模式，"word" 或 "sentence"
            
        Returns:
            文件信息字典，包含 filename 和 content
        """
        if language == "objc":
            content = self.generate_objc_file(string_count, mode)
            filename = "ABStringConstants.m"
        else:
            content = self.generate_cpp_file(string_count, mode)
            filename = "ABStringConstants.cpp"
        
        return {
            "filename": filename,
            "content": content
        }
