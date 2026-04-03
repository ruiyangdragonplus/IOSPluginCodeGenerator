"""
文件写入器模块
负责创建输出目录、写入文件、处理覆盖策略
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime


class FileWriter:
    """文件写入器类"""
    
    def __init__(self, output_dir: str, overwrite: bool = False):
        """
        初始化文件写入器
        
        Args:
            output_dir: 输出目录
            overwrite: 是否允许覆盖已存在的文件
        """
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.written_files: List[str] = []
        self.skipped_files: List[str] = []
    
    def ensure_output_dir(self) -> None:
        """确保输出目录存在，不存在则创建"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
    
    def write_file(
        self,
        filename: str,
        content: str,
        check_exists: bool = True
    ) -> bool:
        """
        写入文件
        
        Args:
            filename: 文件名
            content: 文件内容
            check_exists: 是否检查文件已存在
            
        Returns:
            是否写入成功
        """
        # 确保输出目录存在
        self.ensure_output_dir()
        
        # 构建完整路径
        file_path = os.path.join(self.output_dir, filename)
        
        # 检查文件是否已存在
        if check_exists and os.path.exists(file_path):
            if not self.overwrite:
                self.skipped_files.append(file_path)
                return False
        
        # 写入文件
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.written_files.append(file_path)
            return True
        except Exception as e:
            print(f"写入文件失败：{file_path}, 错误：{e}")
            return False
    
    def write_files(self, files: List[Dict[str, str]]) -> Dict[str, int]:
        """
        批量写入文件
        
        Args:
            files: 文件列表，每个元素包含 filename 和 content
            
        Returns:
            写入统计 {written: 数量，skipped: 数量}
        """
        written = 0
        skipped = 0
        
        for file_info in files:
            filename = file_info.get("filename", "")
            content = file_info.get("content", "")
            
            if self.write_file(filename, content):
                written += 1
            else:
                skipped += 1
        
        return {
            "written": written,
            "skipped": skipped
        }
    
    def get_written_files(self) -> List[str]:
        """获取已写入的文件列表"""
        return self.written_files
    
    def get_skipped_files(self) -> List[str]:
        """获取被跳过的文件列表"""
        return self.skipped_files
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取写入摘要
        
        Returns:
            写入摘要
        """
        return {
            "output_dir": self.output_dir,
            "written_count": len(self.written_files),
            "skipped_count": len(self.skipped_files),
            "overwrite_enabled": self.overwrite,
            "timestamp": datetime.now().isoformat()
        }
    
    def print_summary(self) -> None:
        """打印写入摘要到控制台"""
        summary = self.get_summary()
        print("\n=== 文件写入摘要 ===")
        print(f"输出目录：{summary['output_dir']}")
        print(f"写入文件数：{summary['written_count']}")
        print(f"跳过文件数：{summary['skipped_count']}")
        print(f"覆盖模式：{'开启' if summary['overwrite_enabled'] else '关闭'}")
        
        if self.written_files:
            print("\n已写入文件:")
            for f in self.written_files:
                print(f"  ✓ {f}")
        
        if self.skipped_files:
            print("\n跳过文件:")
            for f in self.skipped_files:
                print(f"  ⊘ {f}")
