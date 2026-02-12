import logging
import sys
from datetime import datetime
from typing import Any


class Logger:
    """日志工具类"""
    
    def __init__(self, name: str = 'monitor_page', level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 控制台handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # 格式化
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """记录信息"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录警告"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """记录错误"""
        self.logger.error(message, exc_info=exc_info)
    
    def debug(self, message: str):
        """记录调试信息"""
        self.logger.debug(message)


# 全局日志实例
logger = Logger()