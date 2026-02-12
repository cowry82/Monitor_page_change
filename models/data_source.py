from typing import List, Dict, Any, Tuple
from collections import Counter
import praw
import requests


class DataSource:
    """数据源基类"""
    
    def fetch(self) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
        """获取数据，返回(代币列表, 代币详情字典)"""
        raise NotImplementedError


class RedditDataSource(DataSource):
    """Reddit数据源"""
    
    def __init__(self, client_id: str, client_secret: str, user_agent: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
    
    def fetch(self) -> List[str]:
        """获取Reddit文本数据"""
        if not self.client_id:
            return []
        
        texts = []
        
        try:
            reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
            )
            
            subs = ["cryptocurrency", "ethtrader", "CryptoMoonShots"]
            
            for sub in subs:
                for post in reddit.subreddit(sub).hot(limit=80):
                    texts.append(post.title)
                    if post.selftext:
                        texts.append(post.selftext)
            
        except Exception as e:
            print(f"Reddit error: {e}")
        
        return texts


class CoinGeckoDataSource(DataSource):
    """CoinGecko数据源"""
    
    def __init__(self, api_url: str = "https://api.coingecko.com/api/v3"):
        self.api_url = api_url
    
    def fetch(self) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
        """获取CoinGecko趋势代币"""
        url = f"{self.api_url}/search/trending"
        
        tokens = []
        token_details = {}
        
        try:
            r = requests.get(url, timeout=10)
            data = r.json()
            
            for coin in data["coins"]:
                symbol = coin["item"]["symbol"].upper()
                name = coin["item"]["name"]
                icon_url = coin["item"].get("large", "")
                tokens.append(symbol)
                token_details[symbol] = {
                    "name": name,
                    "icon_url": icon_url
                }
            
        except Exception as e:
            print(f"CoinGecko error: {e}")
        
        return tokens, token_details


class DexScreenerDataSource(DataSource):
    """DexScreener数据源"""
    
    def __init__(self, api_url: str = "https://api.dexscreener.com/latest/dex/search"):
        self.api_url = api_url
    
    def fetch(self) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
        """获取DexScreener热门交易对"""
        url = self.api_url + "?q=sol"
        
        tokens = []
        token_details = {}
        
        try:
            r = requests.get(url, timeout=10)
            pairs = r.json().get("pairs", [])[:40]
            
            for p in pairs:
                symbol = p.get("baseToken", {}).get("symbol", "").upper()
                if symbol:
                    tokens.append(symbol)
                    if symbol not in token_details:
                        token_details[symbol] = {
                            "name": p.get("baseToken", {}).get("name", ""),
                            "icon_url": p.get("info", {}).get("imageUrl", "")
                        }
            
        except Exception as e:
            print(f"DexScreener error: {e}")
        
        return tokens, token_details


class TextAnalyzer:
    """文本分析器"""
    
    TOKEN_PATTERN = r"\$[A-Za-z0-9]+"
    HASHTAG_PATTERN = r"#[A-Za-z0-9_]+"
    
    def __init__(self, narratives: Dict[str, List[str]]):
        self.narratives = narratives
    
    def analyze(self, texts: List[str]) -> Tuple[Counter, Counter, Counter]:
        """分析文本，返回(代币计数, 标签计数, 叙事计数)"""
        import re
        
        tokens = []
        hashtags = []
        narratives = Counter()
        
        for t in texts:
            tokens += re.findall(self.TOKEN_PATTERN, t)
            hashtags += re.findall(self.HASHTAG_PATTERN, t)
            
            lower = t.lower()
            for n, words in self.narratives.items():
                if any(w in lower for w in words):
                    narratives[n] += 1
        
        token_counter = Counter([t.replace("$", "").upper() for t in tokens])
        hashtag_counter = Counter(hashtags)
        
        return token_counter, hashtag_counter, narratives


class AlphaScoreCalculator:
    """Alpha分数计算器"""
    
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights
    
    def calculate(self, reddit_tokens: Counter, cg_tokens: List[str], 
                dex_tokens: List[str]) -> Counter:
        """计算Alpha分数"""
        from collections import defaultdict
        
        scores = defaultdict(float)
        
        reddit_weight = self.weights.get("reddit", 1.0)
        coingecko_weight = self.weights.get("coingecko", 1.5)
        dexscreener_weight = self.weights.get("dexscreener", 0.7)
        
        for t, c in reddit_tokens.items():
            scores[t] += c * reddit_weight
        
        for t in cg_tokens:
            scores[t] += coingecko_weight
        
        for t in dex_tokens:
            scores[t] += dexscreener_weight
        
        return Counter(scores)
