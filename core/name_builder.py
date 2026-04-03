"""
命名构建器模块
负责生成 PascalCase 类名、camelCase 方法名/属性名，并进行唯一性检查
"""

import random
from typing import Dict, List, Any, Optional, Tuple

from .state_store import StateStore


class NameBuilder:
    """命名构建器类"""
    
    def __init__(self, vocabulary: Dict[str, Any], state_store: StateStore, class_prefix: str = ""):
        """
        初始化命名构建器
        
        Args:
            vocabulary: 词库字典
            state_store: 状态存储实例
            class_prefix: 类名前缀
        """
        self.vocabulary = vocabulary
        self.state_store = state_store
        self.class_prefix = class_prefix
        self.random = random.Random()
    
    def set_seed(self, seed: int) -> None:
        """
        设置随机种子
        
        Args:
            seed: 随机种子
        """
        self.random.seed(seed)
    
    def generate_class_name(self) -> Optional[str]:
        """
        生成唯一的 PascalCase 类名
        
        类名组成：[classPrefix] + class.prefix + class.middle + class.suffixNoun
        
        Returns:
            生成的类名，如果无法生成唯一名称则返回 None
        """
        class_vocab = self.vocabulary.get("class", {})
        prefixes = class_vocab.get("prefix", [])
        middles = class_vocab.get("middle", [])
        suffixes = class_vocab.get("suffixNoun", [])
        
        if not prefixes or not middles or not suffixes:
            return None
        
        max_attempts = 100
        for _ in range(max_attempts):
            prefix = self.random.choice(prefixes)
            middle = self.random.choice(middles)
            suffix = self.random.choice(suffixes)
            
            # 构建类名
            class_name = f"{self.class_prefix}{prefix}{middle}{suffix}"
            
            # 检查是否已使用
            if not self.state_store.is_class_name_used(class_name):
                # 标记为已使用
                self.state_store.mark_class_name_used(class_name)
                return class_name
        
        return None
    
    def generate_method_name(self) -> Optional[str]:
        """
        生成唯一的 camelCase 方法名
        
        方法名组成：method.verb + method.object + method.suffix
        
        Returns:
            生成的方法名，如果无法生成唯一名称则返回 None
        """
        method_vocab = self.vocabulary.get("method", {})
        verbs = method_vocab.get("verb", [])
        objects = method_vocab.get("object", [])
        suffixes = method_vocab.get("suffix", [""])
        
        if not verbs or not objects:
            return None
        
        max_attempts = 100
        for _ in range(max_attempts):
            verb = self.random.choice(verbs)
            obj = self.random.choice(objects)
            suffix = self.random.choice(suffixes) if suffixes else ""
            
            # 构建方法名（camelCase，动词开头）
            method_name = f"{verb}{obj}{suffix}"
            
            # 检查是否已使用
            if not self.state_store.is_method_name_used(method_name):
                # 标记为已使用
                self.state_store.mark_method_name_used(method_name)
                return method_name
        
        return None
    
    def generate_property_name(self) -> Optional[str]:
        """
        生成属性名（不要求全局唯一，但类内不能重复）
        
        属性名组成：property.adjective + property.noun
        
        Returns:
            生成的属性名
        """
        prop_vocab = self.vocabulary.get("property", {})
        adjectives = prop_vocab.get("adjective", [])
        nouns = prop_vocab.get("noun", [])
        
        if not adjectives or not nouns:
            return None
        
        adjective = self.random.choice(adjectives)
        noun = self.random.choice(nouns)
        
        return f"{adjective}{noun}"
    
    def generate_method_names(self, count: int, exclude: Optional[List[str]] = None) -> List[str]:
        """
        生成多个唯一的方法名
        
        Args:
            count: 需要生成的数量
            exclude: 额外排除的方法名列表
            
        Returns:
            生成的方法名列表
        """
        if exclude is None:
            exclude = []
        
        method_names = []
        max_attempts = count * 10
        
        for _ in range(max_attempts):
            if len(method_names) >= count:
                break
            
            method_name = self.generate_method_name()
            if method_name and method_name not in exclude:
                method_names.append(method_name)
        
        return method_names
    
    def generate_property_names(self, count: int, exclude: Optional[List[str]] = None) -> List[str]:
        """
        生成多个属性名
        
        Args:
            count: 需要生成的数量
            exclude: 额外排除的属性名列表
            
        Returns:
            生成的属性名列表
        """
        if exclude is None:
            exclude = []
        
        property_names = []
        max_attempts = count * 10
        
        for _ in range(max_attempts):
            if len(property_names) >= count:
                break
            
            prop_name = self.generate_property_name()
            if prop_name and prop_name not in exclude:
                property_names.append(prop_name)
        
        return property_names
    
    def get_available_class_name_combos(self) -> int:
        """
        计算可用的类名组合数量
        
        Returns:
            可用组合数
        """
        class_vocab = self.vocabulary.get("class", {})
        prefixes = len(class_vocab.get("prefix", []))
        middles = len(class_vocab.get("middle", []))
        suffixes = len(class_vocab.get("suffixNoun", []))
        
        total_combos = prefixes * middles * suffixes
        used_count = len(self.state_store.get_used_class_names())
        
        return max(0, total_combos - used_count)
    
    def get_available_method_name_combos(self) -> int:
        """
        计算可用的方法名组合数量
        
        Returns:
            可用组合数
        """
        method_vocab = self.vocabulary.get("method", {})
        verbs = len(method_vocab.get("verb", []))
        objects = len(method_vocab.get("object", []))
        suffixes = len(method_vocab.get("suffix", [""]))
        
        total_combos = verbs * objects * suffixes
        used_count = len(self.state_store.get_used_method_names())
        
        return max(0, total_combos - used_count)
