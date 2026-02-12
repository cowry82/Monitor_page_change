import requests
import praw
import re
from collections import Counter, defaultdict

# =========================
# Reddit API（填你自己的）
# =========================
REDDIT_CLIENT_ID = ""
REDDIT_CLIENT_SECRET = ""
REDDIT_USER_AGENT = "web3-alpha-tracker"

# =========================
# Narrative 关键词库
# =========================
NARRATIVES = {
    "AI": ["ai", "agent", "llm", "gpt"],
    "RWA": ["rwa", "real world asset"],
    "DePIN": ["depin", "decentralized physical"],
    "L2": ["layer2", "l2", "rollup"],
    "Restaking": ["restake", "eigen"],
    "Meme": ["meme", "pepe", "doge"],
    "GameFi": ["gamefi", "gaming", "play to earn"],
    "DeFi": ["defi", "yield", "dex", "amm"],
}

# =========================
# 正则提取
# =========================
TOKEN_PATTERN = r"\$[A-Za-z0-9]+"
HASHTAG_PATTERN = r"#[A-Za-z0-9_]+"


# =========================
# Reddit
# =========================
def fetch_reddit():
    texts = []

    if not REDDIT_CLIENT_ID:
        print("⚠️ Reddit not configured")
        return texts

    print("📡 Reddit...")

    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )

    subs = ["cryptocurrency", "ethtrader", "CryptoMoonShots"]

    for s in subs:
        for post in reddit.subreddit(s).hot(limit=80):
            texts.append(post.title)
            if post.selftext:
                texts.append(post.selftext)

    print("✅ Reddit texts:", len(texts))
    return texts


# =========================
# CoinGecko Trending
# =========================
def fetch_coingecko():
    print("📡 CoinGecko...")
    url = "https://api.coingecko.com/api/v3/search/trending"
    r = requests.get(url, timeout=10)

    tokens = []

    for coin in r.json()["coins"]:
        symbol = coin["item"]["symbol"]
        tokens.append(symbol.upper())

    print("✅ CoinGecko tokens:", len(tokens))
    return tokens


# =========================
# DexScreener
# =========================
def fetch_dex():
    print("📡 DexScreener...")

    url = "https://api.dexscreener.com/latest/dex/search?q=sol"
    r = requests.get(url, timeout=10)

    tokens = []

    pairs = r.json().get("pairs", [])[:40]

    for p in pairs:
        symbol = p.get("baseToken", {}).get("symbol")
        if symbol:
            tokens.append(symbol.upper())

    print("✅ Dex tokens:", len(tokens))
    return tokens


# =========================
# 文本分析
# =========================
def analyze_texts(texts):

    tokens = []
    hashtags = []
    narratives = Counter()

    for t in texts:
        tokens += re.findall(TOKEN_PATTERN, t)
        hashtags += re.findall(HASHTAG_PATTERN, t)

        lower = t.lower()
        for n, words in NARRATIVES.items():
            if any(w in lower for w in words):
                narratives[n] += 1

    token_counter = Counter([t.replace("$", "").upper() for t in tokens])
    hashtag_counter = Counter(hashtags)

    return token_counter, hashtag_counter, narratives


# =========================
# Alpha Score
# =========================
def build_alpha_scores(reddit_tokens, cg_tokens, dex_tokens):

    scores = defaultdict(float)

    for t, c in reddit_tokens.items():
        scores[t] += c * 1.0

    for t in cg_tokens:
        scores[t] += 1.5

    for t in dex_tokens:
        scores[t] += 0.7

    return Counter(scores)


# =========================
# 可视化
# =========================
def heat_bar(score, max_score):
    if max_score == 0:
        return ""
    lvl = int((score / max_score) * 5)
    return "🔥" * max(1, lvl)


def print_dashboard(alpha_tokens, narratives, hashtags):

    print("\n")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🔥 WEB3 ALPHA TREND RADAR")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # Tokens
    print("\n🥇 MOST DISCUSSED TOKENS (Alpha Score)")
    print("Rank  Token    Score   Heat")
    print("--------------------------------")

    max_score = max(alpha_tokens.values()) if alpha_tokens else 1

    for i, (t, s) in enumerate(alpha_tokens.most_common(12), 1):
        print(f"{i:<5} {t:<8} {round(s,2):<7} {heat_bar(s, max_score)}")

    # Narratives
    print("\n🚀 HOTTEST WEB3 NARRATIVES")
    print("Rank  Narrative   Mentions")
    print("--------------------------------")

    for i, (n, c) in enumerate(narratives.most_common(10), 1):
        print(f"{i:<5} {n:<12} {c}")

    # Hashtags
    print("\n📢 TRENDING HASHTAGS")
    print("--------------------------------")

    for tag, c in hashtags.most_common(10):
        print(tag, c)


# =========================
# 主程序
# =========================
def main():

    print("\n🚀 Starting Web3 Alpha Radar\n")

    reddit_texts = fetch_reddit()
    cg_tokens = fetch_coingecko()
    dex_tokens = fetch_dex()

    reddit_tokens, hashtags, narratives = analyze_texts(reddit_texts)

    alpha_scores = build_alpha_scores(
        reddit_tokens,
        cg_tokens,
        dex_tokens,
    )

    print_dashboard(alpha_scores, narratives, hashtags)


if __name__ == "__main__":
    main()
