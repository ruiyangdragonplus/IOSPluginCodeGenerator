"""
行数预算模块
负责总行数分配、类级/文件级预算控制、方法体复杂度分级
"""

import random
from typing import Dict, List, Any, Tuple


class LineBudget:
    """行数预算类"""
    
    # 方法体复杂度分级对应的行数范围
    COMPLEXITY_LEVELS = {
        1: (1, 3),    # Level 1：简单方法
        2: (4, 8),    # Level 2：中等方法
        3: (8, 15),   # Level 3：复杂方法
    }
    
    def __init__(
        self,
        total_line_range: Tuple[int, int],
        lines_per_class_range: Tuple[int, int],
        methods_per_class_range: Tuple[int, int],
        properties_per_class_range: Tuple[int, int],
        class_count: int
    ):
        """
        初始化行数预算
        
        Args:
            total_line_range: 总输出行数范围 (min, max)
            lines_per_class_range: 单类行数范围 (min, max)
            methods_per_class_range: 每类方法数量范围 (min, max)
            properties_per_class_range: 每类属性数量范围 (min, max)
            class_count: 生成类个数
        """
        self.total_line_min, self.total_line_max = total_line_range
        self.lines_per_class_min, self.lines_per_class_max = lines_per_class_range
        self.methods_per_class_min, self.methods_per_class_max = methods_per_class_range
        self.properties_per_class_min, self.properties_per_class_max = properties_per_class_range
        self.class_count = class_count
        
        self.random = random.Random()
        self.class_budgets: List[Dict[str, Any]] = []
        self.remaining_total = self.total_line_max
    
    def set_seed(self, seed: int) -> None:
        """
        设置随机种子
        
        Args:
            seed: 随机种子
        """
        self.random.seed(seed)
    
    def allocate_budgets(self) -> List[Dict[str, Any]]:
        """
        为每个类分配行数预算
        
        Returns:
            每个类的预算配置列表
        """
        self.class_budgets = []
        remaining_classes = self.class_count
        remaining_lines = self.total_line_max
        
        for i in range(self.class_count):
            remaining_classes -= 1
            
            # 计算当前类的目标行数
            if remaining_classes == 0:
                # 最后一个类，使用剩余行数
                target_lines = remaining_lines
            else:
                # 平均分配剩余行数
                avg_lines = remaining_lines / (remaining_classes + 1)
                # 在范围内随机
                min_lines = max(self.lines_per_class_min, int(avg_lines * 0.7))
                max_lines = min(self.lines_per_class_max, int(avg_lines * 1.3))
                # 确保 min_lines 不超过 max_lines
                min_lines = min(min_lines, max_lines)
                target_lines = self.random.randint(min_lines, max_lines)
            
            # 确保不超过总行数
            target_lines = min(target_lines, remaining_lines)
            
            # 分配方法和属性数量
            methods_count = self.random.randint(
                self.methods_per_class_min,
                self.methods_per_class_max
            )
            properties_count = self.random.randint(
                self.properties_per_class_min,
                self.properties_per_class_max
            )
            
            # 计算每行预算
            budget = {
                "class_index": i,
                "target_lines": target_lines,
                "methods_count": methods_count,
                "properties_count": properties_count,
                "lines_per_method": self._calculate_lines_per_method(target_lines, methods_count, properties_count)
            }
            
            self.class_budgets.append(budget)
            remaining_lines -= target_lines
        
        return self.class_budgets
    
    def _calculate_lines_per_method(self, total_lines: int, methods_count: int, properties_count: int) -> float:
        """
        计算每个方法的平均行数
        
        Args:
            total_lines: 总行数
            methods_count: 方法数量
            properties_count: 属性数量
            
        Returns:
            每个方法的平均行数
        """
        # 估算属性声明占用的行数（约 2 行/属性）
        property_lines = properties_count * 2
        
        # 估算类声明、导入等固定开销（约 10 行）
        fixed_overhead = 10
        
        # 剩余行数分配给方法
        available_for_methods = max(0, total_lines - property_lines - fixed_overhead)
        
        if methods_count > 0:
            return available_for_methods / methods_count
        return 0
    
    def get_method_complexity(self, target_lines: float) -> int:
        """
        根据目标行数确定方法复杂度等级
        
        Args:
            target_lines: 目标行数
            
        Returns:
            复杂度等级 (1-3)
        """
        if target_lines <= 3:
            return 1
        elif target_lines <= 8:
            return 2
        else:
            return 3
    
    def get_method_lines(self, complexity: int) -> Tuple[int, int]:
        """
        获取指定复杂度的方法行数范围
        
        Args:
            complexity: 复杂度等级
            
        Returns:
            行数范围 (min, max)
        """
        return self.COMPLEXITY_LEVELS.get(complexity, (1, 3))
    
    def get_class_budget(self, index: int) -> Dict[str, Any]:
        """
        获取指定类的预算
        
        Args:
            index: 类索引
            
        Returns:
            预算配置
        """
        if 0 <= index < len(self.class_budgets):
            return self.class_budgets[index]
        return {}
    
    def get_total_allocated(self) -> int:
        """
        获取已分配的总行数
        
        Returns:
            已分配行数
        """
        return sum(budget["target_lines"] for budget in self.class_budgets)
    
    def adjust_budget(self, index: int, actual_lines: int) -> None:
        """
        根据实际行数调整预算
        
        Args:
            index: 类索引
            actual_lines: 实际行数
        """
        if 0 <= index < len(self.class_budgets):
            budget = self.class_budgets[index]
            diff = actual_lines - budget["target_lines"]
            budget["actual_lines"] = actual_lines
            budget["line_diff"] = diff
