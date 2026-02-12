import json
import os
from typing import Dict, Any, Optional


class Config:
    """Configuration management class"""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration"""
        if not self._config:
            self._load_config()
    
    def _load_config(self):
        """Load configuration file"""
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration item"""
        return self._config.get(key, default)
    
    def get_reddit_config(self) -> Dict[str, str]:
        """Get Reddit configuration"""
        data_sources = self.get('data_sources', {})
        reddit_config = data_sources.get('reddit', {})
        return {
            'client_id': reddit_config.get('client_id', ''),
            'client_secret': reddit_config.get('client_secret', ''),
            'user_agent': reddit_config.get('user_agent', 'web3-alpha-tracker')
        }
    
    def get_narratives(self) -> Dict[str, list]:
        """Get narrative keywords configuration"""
        return self.get('narratives', {})
    
    def get_weights(self) -> Dict[str, float]:
        """Get data source weights configuration"""
        weights = {}
        data_sources = self.get('data_sources', {})
        for source_name, source_config in data_sources.items():
            if source_config.get('enabled', True):
                weights[source_name] = source_config.get('weight', 1.0)
        return weights if weights else {
            'reddit': 1.0,
            'coingecko': 1.5,
            'dexscreener': 0.7
        }
    
    def get_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """Get data sources configuration"""
        return self.get('data_sources', {
            'reddit': {'enabled': True, 'weight': 1.0, 'client_id': '', 'client_secret': '', 'user_agent': 'web3-alpha-tracker'},
            'coingecko': {'enabled': True, 'weight': 1.5, 'api_url': 'https://api.coingecko.com/api/v3'},
            'dexscreener': {'enabled': True, 'weight': 0.7, 'api_url': 'https://api.dexscreener.com/latest/dex/search'}
        })
    
    def get_lark_webhook_url(self) -> Optional[str]:
        """Get Lark webhook URL"""
        return self.get('lark_webhook_url')
    
    def get_monitor_urls(self) -> list:
        """Get monitor URL list"""
        return self.get('monitor_urls', [])


# Global configuration instance
config = Config()
