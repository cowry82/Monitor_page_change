import hashlib
from typing import Any


def calculate_hash(content: str) -> str:
    """计算内容的MD5哈希值"""
    return hashlib.md5(content.encode()).hexdigest()


def format_date(date_str: str, format_type: str = 'short') -> str:
    """格式化日期字符串"""
    from datetime import datetime
    
    try:
        if format_type == 'short':
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M")
        elif format_type == 'full':
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        else:
            return date_str
    except:
        return date_str


def truncate_string(s: str, max_length: int = 100) -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s
    return s[:max_length] + '...'


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """安全获取字典值"""
    return dictionary.get(key, default)


def validate_url(url: str) -> bool:
    """验证URL格式"""
    import re
    pattern = re.compile(
        r'^(?:http|ftp)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
        r'localhost|' 
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(pattern, url) is not None


def sanitize_filename(filename: str) -> str:
    """清理文件名"""
    import re
    # 移除非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # 限制长度
    return filename[:255]


def format_number(num: float, decimals: int = 2) -> str:
    """格式化数字"""
    return f"{num:.{decimals}f}"


def calculate_percentage(value: float, total: float) -> float:
    """计算百分比"""
    if total == 0:
        return 0.0
    return (value / total) * 100