# Monitor Page

一个功能完整的Web监控和Web3 Alpha趋势分析工具，采用分层架构设计，便于功能迭代和维护。

## 项目结构

```
monitor_page/
├── config/                 # 配置管理
│   ├── __init__.py
│   └── config.py          # 配置管理类
├── models/                 # 数据模型层
│   ├── __init__.py
│   ├── database.py         # 数据库模型
│   └── data_source.py      # 数据源模型
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── web3_alpha_service.py    # Web3 Alpha分析服务
│   └── web_monitor_service.py   # Web监控服务
├── api/                    # API接口层
│   ├── __init__.py
│   └── web3_alpha_api.py       # Web3 Alpha API
├── utils/                  # 工具函数层
│   ├── __init__.py
│   ├── logger.py          # 日志工具
│   └── helpers.py         # 辅助函数
├── scripts/                # 脚本文件
│   ├── run_web3_alpha.py  # Web3 Alpha分析脚本
│   └── run_web_monitor.py # Web监控脚本
├── static/                 # 静态文件
├── config.json            # 配置文件
├── requirements.txt        # 依赖管理
├── main.py               # 主入口文件
├── web3_alpha_dashboard.html  # Web3 Alpha仪表板
└── README.md             # 项目文档
```

## 功能特性

### Web3 Alpha趋势分析
- 多数据源整合：Reddit、CoinGecko、DexScreener
- 智能分析：自动识别热门代币和叙事趋势
- Alpha分数计算：基于多维度数据计算代币热度
- 数据持久化：使用SQLite存储历史数据
- 可视化展示：直观的热度仪表板

### Web监控
- 网页内容变更检测
- 多种元素类型监控（文本、图片、脚本、样式、链接）
- 飞书通知集成
- 支持本地文件和网络URL

### API服务
- RESTful API接口
- 支持时间维度数据查询
- 健康检查接口
- JSON格式响应

## 安装

### 环境要求
- Python 3.9+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

编辑 `config.json` 文件，配置必要的参数：

```json
{
    "lark_webhook_url": "your-webhook-url",
    "monitor_urls": ["url1", "url2"],
    "reddit_client_id": "your-client-id",
    "reddit_client_secret": "your-client-secret",
    "reddit_user_agent": "web3-alpha-tracker",
    "narratives": {
        "AI": ["ai", "agent", "llm", "gpt"],
        "RWA": ["rwa", "real world asset"],
        "DePIN": ["depin", "decentralized physical"],
        "L2": ["layer2", "l2", "rollup"],
        "Restaking": ["restake", "eigen"],
        "Meme": ["meme", "pepe", "doge"],
        "GameFi": ["gamefi", "gaming", "play to earn"],
        "DeFi": ["defi", "yield", "dex", "amm"]
    },
    "weights": {
        "reddit": 1.0,
        "coingecko": 1.5,
        "dexscreener": 0.7
    }
}
```

## 使用方法

### 命令行接口

#### 运行Web3 Alpha分析

```bash
python main.py alpha
```

#### 运行Web监控

```bash
python main.py monitor
```

#### 启动API服务器

```bash
python main.py api --port 8080 --host 0.0.0.0
```

### 直接运行脚本

#### Web3 Alpha分析

```bash
python scripts/run_web3_alpha.py
```

#### Web监控

```bash
python scripts/run_web_monitor.py
```

### API接口

#### 获取代币数据

```bash
curl "http://localhost:8080/api/tokens?time_range=day&limit=100"
```

参数：
- `time_range`: 时间范围，可选值：hour, day, week, month
- `limit`: 返回数量限制，默认100

#### 获取叙事数据

```bash
curl "http://localhost:8080/api/narratives"
```

#### 获取标签数据

```bash
curl "http://localhost:8080/api/hashtags"
```

#### 健康检查

```bash
curl "http://localhost:8080/api/health"
```

### Web仪表板

在浏览器中打开 `web3_alpha_dashboard.html` 文件，查看可视化的代币趋势数据。

## 分层架构说明

### 配置层 (config/)
负责管理所有配置信息，包括：
- 数据源配置
- API密钥
- 权重设置
- 监控URL列表

### 数据模型层 (models/)
定义数据结构和数据访问接口：
- `DatabaseManager`: 数据库管理基类
- `TokenModel`: Web3 Alpha数据模型
- `WebMonitorModel`: Web监控数据模型
- `DataSource`: 数据源基类
- `TextAnalyzer`: 文本分析器
- `AlphaScoreCalculator`: Alpha分数计算器

### 业务逻辑层 (services/)
实现核心业务逻辑：
- `Web3AlphaService`: Web3 Alpha趋势分析服务
- `WebMonitorService`: Web监控服务

### API接口层 (api/)
提供HTTP API接口：
- `Web3AlphaAPI`: Web3 Alpha API接口

### 工具函数层 (utils/)
提供通用工具函数：
- `Logger`: 日志工具
- `helpers`: 辅助函数（哈希计算、日期格式化等）

### 脚本层 (scripts/)
提供可执行的脚本文件：
- `run_web3_alpha.py`: Web3 Alpha分析脚本
- `run_web_monitor.py`: Web监控脚本

## 数据库

项目使用SQLite数据库，包含以下表：

### web3_alpha.db
- `tokens`: 代币信息
- `narratives`: 叙事信息
- `hashtags`: 标签信息

### web_monitor.db
- `web_pages`: 网页信息
- `page_elements`: 页面元素信息

## 定时任务

使用cron或任务调度器定期运行：

```bash
# 每小时运行一次Web3 Alpha分析
0 * * * * cd /path/to/monitor_page && python main.py alpha

# 每30分钟运行一次Web监控
*/30 * * * * cd /path/to/monitor_page && python main.py monitor
```

## 开发指南

### 添加新的数据源

1. 在 `models/data_source.py` 中创建新的数据源类，继承 `DataSource`
2. 在 `services/web3_alpha_service.py` 中集成新的数据源
3. 在 `config.json` 中添加相关配置

### 添加新的API端点

1. 在 `api/web3_alpha_api.py` 中添加新的路由方法
2. 在 `Web3AlphaAPI._setup_routes()` 中注册路由

### 添加新的功能模块

1. 在 `services/` 中创建新的服务类
2. 在 `scripts/` 中创建对应的脚本文件
3. 在 `main.py` 中添加命令行接口

## 故障排除

### SSL证书错误

```bash
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

### 数据库锁定

确保没有其他程序正在访问数据库文件。

### API端口被占用

修改 `main.py` 中的默认端口，或使用 `--port` 参数指定其他端口。

## 许可证

本项目仅供学习和研究使用。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 更新日志

### v2.0.0 (2026-02-12)
- 重构为分层架构
- 添加统一的命令行接口
- 改进配置管理
- 增强错误处理和日志记录
- 优化代码结构和可维护性

### v1.0.0
- 初始版本
- Web3 Alpha趋势分析
- Web页面监控
- API服务
- Web仪表板
