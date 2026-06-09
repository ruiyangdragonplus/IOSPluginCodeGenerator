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
    
    def _word_pool(self) -> List[str]:
        """词库中所有命名词的合并池（prefix + middle + suffixNoun）。"""
        cv = self.vocabulary.get("class", {})
        return cv.get("prefix", []) + cv.get("middle", []) + cv.get("suffixNoun", [])

    def generate_random_content(self, mode: str = "word") -> str:
        """
        从词库随机组合生成内容（高多样性：使用全部三类词的合并池，多词组合）。

        Args:
            mode: "word"（2-3 词）或 "sentence"（3-6 词）

        Returns:
            生成的 String 内容
        """
        pool = self._word_pool()
        if not pool:
            return "Default String Value"

        # word: 2-3 词；sentence: 3-6 词。组合空间 ~ pool^n，远大于旧版的 1-2 词。
        n = self.random.randint(3, 6) if mode == "sentence" else self.random.randint(2, 3)
        parts = [self.random.choice(pool) for _ in range(n)]
        return " ".join(parts)

    def _unique_content(self, mode: str, used: set) -> str:
        """生成一个与 used 集合不重复的内容；碰撞时追加词，最终必要时追加序号兜底。"""
        pool = self._word_pool()
        content = self.generate_random_content(mode)
        attempts = 0
        # 碰撞则追加一个词扩展，扩大区分度
        while content in used and attempts < 20 and pool:
            content = content + " " + self.random.choice(pool)
            attempts += 1
        # 仍冲突则以序号兜底，保证 100% 唯一
        if content in used:
            content = f"{content} {len(used)}"
        used.add(content)
        return content
    
    def generate_string_constant(self, index: int, mode: str = "word", prefix: str = "AB") -> Dict[str, str]:
        """
        生成单个 String 常量
        
        Args:
            index: 常量索引
            mode: 生成模式，"word" 或 "sentence"
            prefix: 常量名前缀
            
        Returns:
            包含 constant_name 和 content 的字典
        """
        content = self.generate_random_content(mode)
        return {
            "constant_name": f"{prefix}StringConstant_{index}",
            "content": content
        }
    
    def generate_objc_file(self, string_count: int, mode: str = "word", prefix: str = "MX11",
                           output_filename: str = "MX11StringConstants") -> str:
        """
        生成 Objective-C 格式的 String 常量文件
        
        Args:
            string_count: String 数量
            mode: 生成模式
            prefix: 常量名前缀
            output_filename: 输出文件名
            
        Returns:
            文件内容
        """
        lines = []
        
        # 文件头注释
        lines.append(f"// {output_filename}.m")
        lines.append("#import <Foundation/Foundation.h>")
        lines.append("")
        
        # 生成常量声明 - 使用 NSString* const 格式（去重保证值多样性）
        used: set = set()
        for i in range(string_count):
            content = self._unique_content(mode, used)
            lines.append(f'NSString* const {prefix}StringConstant_{i} = @"{content}";')
        
        lines.append("")
        
        # 生成打印函数
        lines.append(f"void {prefix}PrintStringConstants() {{")
        lines.append("    if (YES) return;")
        
        for i in range(string_count):
            lines.append(f'    NSLog(@"%@", {prefix}StringConstant_{i});')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_cpp_file(self, string_count: int, mode: str = "word", prefix: str = "MX11",
                          output_filename: str = "MX11StringConstants") -> str:
        """
        生成 C++ 格式的 String 常量文件
        
        Args:
            string_count: String 数量
            mode: 生成模式
            prefix: 常量名前缀
            output_filename: 输出文件名
            
        Returns:
            文件内容
        """
        lines = []
        
        # 文件头注释
        lines.append(f"// {output_filename}.cpp")
        lines.append("#include <cstdio>")
        lines.append("")
        
        # 生成常量声明（去重保证值多样性）
        used: set = set()
        for i in range(string_count):
            content = self._unique_content(mode, used)
            lines.append(f'static const char {prefix}StringConstant_{i}[] = "{content}";')
        
        lines.append("")
        
        # 生成打印函数
        lines.append(f"void {prefix}PrintStringConstants() {{")
        lines.append("    if (true) return;")
        
        for i in range(string_count):
            lines.append(f'    printf("%s\\n", {prefix}StringConstant_{i});')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def generate_file(self, string_count: int, language: str = "objc", mode: str = "word",
                      prefix: str = "MX11", output_filename: str = "MX11StringConstants") -> Dict[str, str]:
        """
        生成完整的 String 常量文件
        
        Args:
            string_count: String 数量
            language: 语言选项，"objc" 或 "cpp"
            mode: 生成模式，"word" 或 "sentence"
            prefix: 常量名前缀
            output_filename: 输出文件名
            
        Returns:
            文件信息字典，包含 filename 和 content
        """
        if language == "objc":
            content = self.generate_objc_file(string_count, mode, prefix, output_filename)
            filename = f"{output_filename}.m"
        else:
            content = self.generate_cpp_file(string_count, mode, prefix, output_filename)
            filename = f"{output_filename}.cpp"
        
        return {
            "filename": filename,
            "content": content
        }
