from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from typing import Dict, Any
import os

from services.web3_alpha_service import Web3AlphaService


class Web3AlphaAPI:
    """Web3 Alpha API接口"""
    
    def __init__(self, service: Web3AlphaService):
        self.app = Flask(__name__)
        self.service = service
        
        # Enable CORS for all routes
        CORS(self.app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
        
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由"""
        # Dashboard页面
        self.app.route('/')(self.serve_dashboard)
        self.app.route('/dashboard')(self.serve_dashboard)
        
        # API端点
        self.app.route('/api/tokens', methods=['GET', 'OPTIONS'])(self.get_tokens)
        self.app.route('/api/narratives', methods=['GET', 'OPTIONS'])(self.get_narratives)
        self.app.route('/api/hashtags', methods=['GET', 'OPTIONS'])(self.get_hashtags)
        self.app.route('/api/health', methods=['GET', 'OPTIONS'])(self.health_check)
    
    def serve_dashboard(self):
        """提供Dashboard页面"""
        try:
            # 获取项目根目录
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            dashboard_path = os.path.join(project_root, 'web3_alpha_dashboard.html')
            
            if os.path.exists(dashboard_path):
                return send_from_directory(project_root, 'web3_alpha_dashboard.html')
            else:
                return jsonify({
                    'error': 'Dashboard file not found',
                    'message': f'web3_alpha_dashboard.html does not exist at {dashboard_path}'
                }), 404
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to serve dashboard'
            }), 500
    
    def get_tokens(self):
        """
        获取代币数据
        支持时间筛选参数：
        - time_range: 时间范围，可选值：hour, day, week, month
        - limit: 返回数量限制，默认100
        """
        time_range = request.args.get('time_range', 'day')
        limit = request.args.get('limit', 100, type=int)
        
        try:
            tokens = self.service.get_tokens_by_time_range(time_range, limit)
            
            # 格式化日期
            for token in tokens:
                token['created_at'] = self._format_date(token['created_at'])
            
            return jsonify({
                'data': tokens,
                'total': len(tokens),
                'time_range': time_range,
                'query_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to fetch tokens data'
            }), 500
    
    def get_narratives(self):
        """获取叙事数据"""
        try:
            narratives = self.service.get_narratives()
            
            # 格式化日期
            for narrative in narratives:
                narrative['updated_at'] = self._format_date(narrative['updated_at'])
            
            return jsonify({
                'data': narratives,
                'total': len(narratives)
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to fetch narratives data'
            }), 500
    
    def get_hashtags(self):
        """获取标签数据"""
        try:
            hashtags = self.service.get_hashtags()
            
            # 格式化日期
            for tag in hashtags:
                tag['updated_at'] = self._format_date(tag['updated_at'])
            
            return jsonify({
                'data': hashtags,
                'total': len(hashtags)
            })
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to fetch hashtags data'
            }), 500
    
    def health_check(self):
        """健康检查接口"""
        try:
            # 检查数据库连接
            tokens = self.service.get_tokens_by_time_range('day', 1)
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'database': 'connected'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'database': 'disconnected'
            }), 500
    
    def _format_date(self, date_str: str) -> str:
        """格式化日期字符串"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        except:
            return date_str
    
    def run(self, host: str = '0.0.0.0', port: int = 8080, debug: bool = True):
        """运行Flask应用"""
        self.app.run(host=host, port=port, debug=debug)


def create_app() -> Flask:
    """应用工厂函数"""
    service = Web3AlphaService()
    api = Web3AlphaAPI(service)
    return api.app


if __name__ == '__main__':
    service = Web3AlphaService()
    api = Web3AlphaAPI(service)
    api.run(port=8080)
