"""
状态存储模块
负责加载/保存状态文件，记录已使用的命名、已生成的文件、执行历史

性能优化：使用 set 进行 O(1) 查找，保存时转换为 list 保持 JSON 兼容性
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Any, Optional, Set


class StateStore:
    """状态存储类"""
    
    def __init__(self, state_path: str):
        """
        初始化状态存储
        
        Args:
            state_path: 状态文件路径
        """
        self.state_path = state_path
        # 使用 set 进行 O(1) 查找（内存中）
        self._usedClassNames: Set[str] = set()
        self._usedMethodNames: Set[str] = set()
        self._usedWordCombos: Set[str] = set()
        self._generatedFiles: Set[str] = set()
        # 历史记录保持为 list（有序）
        self._history: List[Dict[str, Any]] = []
        # 原始状态字典（用于保存）
        self.state: Dict[str, Any] = {
            "usedClassNames": [],
            "usedMethodNames": [],
            "usedWordCombos": [],
            "generatedFiles": [],
            "history": []
        }
    
    def load(self) -> Dict[str, Any]:
        """
        加载状态文件
        
        Returns:
            状态字典
            
        Raises:
            FileNotFoundError: 状态文件不存在（首次运行时可能）
        """
        if not os.path.exists(self.state_path):
            # 首次运行，返回空状态
            return self.state
        
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                self.state = json.load(f)
            
            # 确保所有必需字段存在
            self._ensure_fields()
            
            # 从 list 构建 set 索引，实现 O(1) 查找
            self._usedClassNames = set(self.state.get("usedClassNames", []))
            self._usedMethodNames = set(self.state.get("usedMethodNames", []))
            self._usedWordCombos = set(self.state.get("usedWordCombos", []))
            self._generatedFiles = set(self.state.get("generatedFiles", []))
            self._history = self.state.get("history", [])
            
            return self.state
        except json.JSONDecodeError as e:
            # 状态文件损坏，备份并重建
            self._backup_corrupted()
            return self.state
    
    def _ensure_fields(self) -> None:
        """确保状态字典包含所有必需字段"""
        required_fields = [
            "usedClassNames",
            "usedMethodNames", 
            "usedWordCombos",
            "generatedFiles",
            "history"
        ]
        for field in required_fields:
            if field not in self.state:
                self.state[field] = []
    
    def _backup_corrupted(self) -> None:
        """备份损坏的状态文件"""
        if os.path.exists(self.state_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.state_path}.backup_{timestamp}"
            shutil.copy(self.state_path, backup_path)
            print(f"警告：状态文件损坏，已备份至 {backup_path}")
    
    def save(self) -> None:
        """保存状态文件"""
        # 确保目录存在
        state_dir = os.path.dirname(self.state_path)
        if state_dir and not os.path.exists(state_dir):
            os.makedirs(state_dir, exist_ok=True)
        
        # 将 set 转换为 list 以保持 JSON 兼容性
        self.state["usedClassNames"] = sorted(list(self._usedClassNames))
        self.state["usedMethodNames"] = sorted(list(self._usedMethodNames))
        self.state["usedWordCombos"] = sorted(list(self._usedWordCombos))
        self.state["generatedFiles"] = sorted(list(self._generatedFiles))
        self.state["history"] = self._history
        
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def is_class_name_used(self, class_name: str) -> bool:
        """
        检查类名是否已使用（O(1) 时间复杂度）
        
        Args:
            class_name: 类名
            
        Returns:
            是否已使用
        """
        return class_name in self._usedClassNames
    
    def mark_class_name_used(self, class_name: str) -> None:
        """
        标记类名为已使用（O(1) 时间复杂度）
        
        Args:
            class_name: 类名
        """
        self._usedClassNames.add(class_name)
    
    def is_method_name_used(self, method_name: str) -> bool:
        """
        检查方法名是否已使用（O(1) 时间复杂度）
        
        Args:
            method_name: 方法名
            
        Returns:
            是否已使用
        """
        return method_name in self._usedMethodNames
    
    def mark_method_name_used(self, method_name: str) -> None:
        """
        标记方法名为已使用（O(1) 时间复杂度）
        
        Args:
            method_name: 方法名
        """
        self._usedMethodNames.add(method_name)
    
    def is_word_combo_used(self, combo: str) -> bool:
        """
        检查词汇组合是否已使用（O(1) 时间复杂度）
        
        Args:
            combo: 词汇组合
            
        Returns:
            是否已使用
        """
        return combo in self._usedWordCombos
    
    def mark_word_combo_used(self, combo: str) -> None:
        """
        标记词汇组合为已使用（O(1) 时间复杂度）
        
        Args:
            combo: 词汇组合
        """
        self._usedWordCombos.add(combo)
    
    def is_file_generated(self, file_path: str) -> bool:
        """
        检查文件是否已生成（O(1) 时间复杂度）
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否已生成
        """
        return file_path in self._generatedFiles
    
    def mark_file_generated(self, file_path: str) -> None:
        """
        标记文件为已生成（O(1) 时间复杂度）
        
        Args:
            file_path: 文件路径
        """
        self._generatedFiles.add(file_path)
    
    def add_history_entry(self, entry: Dict[str, Any]) -> None:
        """
        添加执行历史记录
        
        Args:
            entry: 历史记录条目
        """
        entry["timestamp"] = datetime.now().isoformat()
        self._history.append(entry)
    
    def get_used_class_names(self) -> List[str]:
        """获取已使用的类名列表"""
        return list(self._usedClassNames)
    
    def get_used_method_names(self) -> List[str]:
        """获取已使用的方法名列表"""
        return list(self._usedMethodNames)
    
    def get_generated_files(self) -> List[str]:
        """获取已生成的文件列表"""
        return list(self._generatedFiles)
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self._history
