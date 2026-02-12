#!/usr/bin/env python3
"""
Monitor Page 主入口文件
提供统一的命令行接口来运行不同的功能模块
"""

import sys
import os
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.run_web3_alpha import main as run_web3_alpha_main
from scripts.run_web_monitor import main as run_web_monitor_main
from api.web3_alpha_api import Web3AlphaAPI
from services.web3_alpha_service import Web3AlphaService
from utils.logger import logger


def run_web3_alpha(args):
    """运行Web3 Alpha分析"""
    logger.info("Starting Web3 Alpha analysis...")
    return run_web3_alpha_main()


def run_web_monitor(args):
    """运行Web监控"""
    logger.info("Starting Web monitoring...")
    return run_web_monitor_main()


def run_api_server(port: int = 8080, host: str = '0.0.0.0'):
    """运行API服务器"""
    logger.info(f"Starting API server on {host}:{port}...")
    service = Web3AlphaService()
    api = Web3AlphaAPI(service)
    api.run(host=host, port=port, debug=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Monitor Page - Web监控和Web3 Alpha趋势分析工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行Web3 Alpha分析
  python3 main.py alpha
  
  # 运行Web监控
  python3 main.py monitor
  
  # 启动API服务器
  python3 main.py api --port 8080
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # Web3 Alpha命令
    alpha_parser = subparsers.add_parser('alpha', help='运行Web3 Alpha趋势分析')
    alpha_parser.set_defaults(func=run_web3_alpha)
    
    # Web监控命令
    monitor_parser = subparsers.add_parser('monitor', help='运行Web页面监控')
    monitor_parser.set_defaults(func=run_web_monitor)
    
    # API服务器命令
    api_parser = subparsers.add_parser('api', help='启动API服务器')
    api_parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    api_parser.add_argument('--port', type=int, default=8080, help='监听端口 (默认: 8080)')
    api_parser.add_argument('--debug', action='store_true', help='启用调试模式')
    api_parser.set_defaults(func=lambda args: run_api_server(args.port, args.host))
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 执行命令
    try:
        result = args.func(args)
        logger.info("Command completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
