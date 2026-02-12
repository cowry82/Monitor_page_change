#!/usr/bin/env python3
"""
Web3 Alpha趋势分析脚本
用于从多个数据源获取数据并分析Web3领域的热门代币和趋势
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.web3_alpha_service import Web3AlphaService
from utils.logger import logger


def main():
    """主函数"""
    try:
        # 创建服务实例
        service = Web3AlphaService()
        
        # 运行分析
        result = service.run_analysis()
        
        logger.info("Web3 Alpha analysis completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Web3 Alpha analysis failed: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    main()