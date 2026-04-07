"""
配置加载器模块
负责读取 JSON 配置文件、校验配置项、填充默认值
"""

import json
import os
from typing import Dict, Any, Optional


class ConfigLoader:
    """配置加载器类"""
    
    # 默认配置值
    DEFAULT_CONFIG = {
        "language": "objc",
        "outputDir": "./output",
        "classCount": 6,
        "totalLineRange": [500, 900],
        "linesPerClassRange": [60, 180],
        "methodsPerClassRange": [4, 8],
        "propertiesPerClassRange": [2, 5],
        "classPrefix": "AB",
        "incremental": True,
        "overwrite": False,
        "randomSeed": 12345,
        "stateFile": "./config/state.json",
        "vocabularyFile": "./config/vocabulary.json"
    }
    
    # 必填字段
    REQUIRED_FIELDS = [
        "language",
        "outputDir",
        "stateFile",
        "vocabularyFile"
    ]
    
    # 有效的语言选项
    VALID_LANGUAGES = ["objc", "cpp", "string"]
    
    def __init__(self, config_path: str):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
    
    def load(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: JSON 格式错误
            ValueError: 配置校验失败
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件不存在：{self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        # 填充默认值
        self._fill_defaults()
        
        # 校验配置
        self._validate()
        
        return self.config
    
    def _fill_defaults(self) -> None:
        """填充默认配置值"""
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in self.config:
                self.config[key] = value
    
    def _validate(self) -> None:
        """
        校验配置项
        
        Raises:
            ValueError: 配置校验失败
        """
        # 检查必填字段
        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                raise ValueError(f"缺少必填配置项：{field}")
        
        # 校验语言选项
        if self.config.get("language") not in self.VALID_LANGUAGES:
            raise ValueError(f"无效的语言选项：{self.config.get('language')}，必须是 {self.VALID_LANGUAGES} 之一")
        
        # 对于 string 模式，使用不同的校验逻辑
        if self.config.get("language") == "string":
            # string 模式需要 stringCount
            if "stringCount" not in self.config:
                self.config["stringCount"] = 1000
            if not isinstance(self.config.get("stringCount"), int) or self.config["stringCount"] <= 0:
                raise ValueError("stringCount 必须是正整数")
        else:
            # 原有校验逻辑
            if "classCount" not in self.config:
                self.config["classCount"] = 6
            if not isinstance(self.config.get("classCount"), int) or self.config["classCount"] <= 0:
                raise ValueError("classCount 必须是正整数")
            
            # 校验范围配置
            self._validate_range("totalLineRange", self.config.get("totalLineRange"))
            self._validate_range("linesPerClassRange", self.config.get("linesPerClassRange"))
            self._validate_range("methodsPerClassRange", self.config.get("methodsPerClassRange"))
            self._validate_range("propertiesPerClassRange", self.config.get("propertiesPerClassRange"))
    
    def _validate_range(self, field_name: str, value: Any) -> None:
        """
        校验范围配置
        
        Args:
            field_name: 字段名称
            value: 字段值
            
        Raises:
            ValueError: 校验失败
        """
        if value is None:
            return
        
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(f"{field_name} 必须是包含两个元素的数组")
        
        if not all(isinstance(x, int) for x in value):
            raise ValueError(f"{field_name} 的元素必须是整数")
        
        if value[0] > value[1]:
            raise ValueError(f"{field_name} 的最小值不能大于最大值")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def override(self, overrides: Dict[str, Any]) -> None:
        """
        覆盖配置值
        
        Args:
            overrides: 要覆盖的配置项
        """
        self.config.update(overrides)
    
    @classmethod
    def load_vocabulary(cls, vocab_path: str) -> Dict[str, Any]:
        """
        加载词库配置
        
        Args:
            vocab_path: 词库文件路径
            
        Returns:
            词库字典
            
        Raises:
            FileNotFoundError: 词库文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        if not os.path.exists(vocab_path):
            raise FileNotFoundError(f"词库文件不存在：{vocab_path}")
        
        with open(vocab_path, 'r', encoding='utf-8') as f:
            return json.load(f)
