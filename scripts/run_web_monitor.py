#!/usr/bin/env python3
"""
Web监控脚本
用于监控网页内容变更并发送通知
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.web_monitor_service import WebMonitorService
from utils.logger import logger


def main():
    """主函数"""
    try:
        # 创建服务实例
        service = WebMonitorService()
        
        # 运行监控
        changes = service.monitor_urls()
        
        if changes:
            logger.info(f"Detected {len(changes)} changes")
        else:
            logger.info("No changes detected")
        
        return changes
        
    except Exception as e:
        logger.error(f"Web monitoring failed: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    main()
