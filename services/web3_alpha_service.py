from typing import List, Dict, Any
from datetime import datetime, timedelta
from collections import Counter

from models.database import TokenModel
from models.data_source import (
    RedditDataSource, CoinGeckoDataSource, DexScreenerDataSource,
    TextAnalyzer, AlphaScoreCalculator
)
from config.config import config


class Web3AlphaService:
    """Web3 Alpha趋势分析服务"""
    
    def __init__(self):
        self.db = TokenModel()
        self.narratives = config.get_narratives()
        self.data_sources_config = config.get_data_sources()
        self.weights = config.get_weights()
        
        # 初始化数据源
        self.sources = {}
        
        # Reddit数据源
        reddit_config = self.data_sources_config.get('reddit', {})
        if reddit_config.get('enabled', True):
            self.sources['reddit'] = RedditDataSource(
                client_id=reddit_config.get('client_id', ''),
                client_secret=reddit_config.get('client_secret', ''),
                user_agent=reddit_config.get('user_agent', 'web3-alpha-tracker')
            )
        
        # CoinGecko数据源
        coingecko_config = self.data_sources_config.get('coingecko', {})
        if coingecko_config.get('enabled', True):
            self.sources['coingecko'] = CoinGeckoDataSource(
                api_url=coingecko_config.get('api_url', 'https://api.coingecko.com/api/v3')
            )
        
        # DexScreener数据源
        dexscreener_config = self.data_sources_config.get('dexscreener', {})
        if dexscreener_config.get('enabled', True):
            self.sources['dexscreener'] = DexScreenerDataSource(
                api_url=dexscreener_config.get('api_url', 'https://api.dexscreener.com/latest/dex/search')
            )
        
        # 初始化分析器
        self.text_analyzer = TextAnalyzer(self.narratives)
        self.score_calculator = AlphaScoreCalculator(self.weights)
    
    def run_analysis(self):
        """运行完整的分析流程"""
        print("\n🚀 Starting Web3 Alpha Radar\n")
        
        # 初始化数据库
        self.db.init_db()
        
        # 获取数据
        reddit_texts = []
        cg_tokens = []
        cg_details = {}
        dex_tokens = []
        dex_details = {}
        
        if 'reddit' in self.sources:
            reddit_texts = self._fetch_reddit()
        if 'coingecko' in self.sources:
            cg_tokens, cg_details = self._fetch_coingecko()
        if 'dexscreener' in self.sources:
            dex_tokens, dex_details = self._fetch_dex()
        
        # 分析文本
        reddit_tokens, hashtags, narratives = self.text_analyzer.analyze(reddit_texts)
        
        # 计算Alpha分数
        alpha_scores = self.score_calculator.calculate(
            reddit_tokens,
            cg_tokens,
            dex_tokens
        )
        
        # 准备数据并保存
        tokens_data = self._prepare_tokens_data(
            alpha_scores, cg_details, dex_details
        )
        
        self.db.save_tokens(tokens_data)
        self.db.save_narratives(dict(narratives.most_common(20)))
        self.db.save_hashtags(dict(hashtags.most_common(20)))
        
        # 打印仪表板
        self._print_dashboard(alpha_scores, narratives, hashtags)
        
        print("\n💾 Data saved to database: web3_alpha.db")
        
        return {
            'tokens': tokens_data,
            'narratives': dict(narratives.most_common(20)),
            'hashtags': dict(hashtags.most_common(20))
        }
    
    def _fetch_reddit(self) -> List[str]:
        """获取Reddit数据"""
        if 'reddit' not in self.sources:
            print("📡 Reddit: Skipped (disabled in config)")
            return []
        print("📡 Reddit...")
        texts = self.sources['reddit'].fetch()
        print(f"✅ Reddit texts: {len(texts)}")
        return texts
    
    def _fetch_coingecko(self) -> tuple:
        """获取CoinGecko数据"""
        if 'coingecko' not in self.sources:
            print("📡 CoinGecko: Skipped (disabled in config)")
            return [], {}
        print("📡 CoinGecko...")
        tokens, details = self.sources['coingecko'].fetch()
        print(f"✅ CoinGecko tokens: {len(tokens)}")
        return tokens, details
    
    def _fetch_dex(self) -> tuple:
        """获取DexScreener数据"""
        if 'dexscreener' not in self.sources:
            print("📡 DexScreener: Skipped (disabled in config)")
            return [], {}
        print("📡 DexScreener...")
        tokens, details = self.sources['dexscreener'].fetch()
        print(f"✅ Dex tokens: {len(tokens)}")
        return tokens, details
    
    def _prepare_tokens_data(self, alpha_scores: Counter, 
                          cg_details: Dict[str, Dict[str, str]],
                          dex_details: Dict[str, Dict[str, str]]) -> List[Dict[str, Any]]:
        """准备代币数据"""
        tokens_data = []
        max_score = max(alpha_scores.values()) if alpha_scores else 1
        
        for rank, (symbol, score) in enumerate(alpha_scores.most_common(50), 1):
            heat_level = int((score / max_score) * 5) if max_score > 0 else 0
            
            token_info = {
                "symbol": symbol,
                "rank": rank,
                "alpha_score": round(score, 2),
                "heat_level": heat_level
            }
            
            # 添加详情
            if symbol in cg_details:
                token_info["name"] = cg_details[symbol]["name"]
                token_info["icon_url"] = cg_details[symbol]["icon_url"]
            elif symbol in dex_details:
                token_info["name"] = dex_details[symbol]["name"]
                token_info["icon_url"] = dex_details[symbol]["icon_url"]
            
            tokens_data.append(token_info)
        
        return tokens_data
    
    def _print_dashboard(self, alpha_tokens: Counter, 
                      narratives: Counter, hashtags: Counter):
        """打印仪表板"""
        print("\n")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔥 WEB3 ALPHA TREND RADAR")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # 代币
        print("\n🥇 MOST DISCUSSED TOKENS (Alpha Score)")
        print("Rank  Token    Score   Heat")
        print("--------------------------------")
        
        max_score = max(alpha_tokens.values()) if alpha_tokens else 1
        
        for i, (t, s) in enumerate(alpha_tokens.most_common(12), 1):
            heat = self._heat_bar(s, max_score)
            print(f"{i:<5} {t:<8} {round(s,2):<7} {heat}")
        
        # 叙事
        print("\n🚀 HOTTEST WEB3 NARRATIVES")
        print("Rank  Narrative   Mentions")
        print("--------------------------------")
        
        for i, (n, c) in enumerate(narratives.most_common(10), 1):
            print(f"{i:<5} {n:<12} {c}")
        
        # 标签
        print("\n📢 TRENDING HASHTAGS")
        print("--------------------------------")
        
        for tag, c in hashtags.most_common(10):
            print(tag, c)
    
    def _heat_bar(self, score: float, max_score: float) -> str:
        """生成热度条"""
        if max_score == 0:
            return ""
        lvl = int((score / max_score) * 5)
        return "🔥" * max(1, lvl)
    
    def get_tokens_by_time_range(self, time_range: str = 'day', 
                              limit: int = 100) -> List[Dict[str, Any]]:
        """按时间范围获取代币数据"""
        now = datetime.now()
        
        if time_range == 'hour':
            start_time = now - timedelta(hours=1)
        elif time_range == 'day':
            start_time = now - timedelta(days=1)
        elif time_range == 'week':
            start_time = now - timedelta(weeks=1)
        elif time_range == 'month':
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)
        
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return self.db.get_tokens_by_time_range(start_time_str, limit)
    
    def get_narratives(self) -> List[Dict[str, Any]]:
        """获取叙事数据"""
        return self.db.get_narratives()
    
    def get_hashtags(self) -> List[Dict[str, Any]]:
        """获取标签数据"""
        return self.db.get_hashtags()
