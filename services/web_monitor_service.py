import requests
import ssl
import urllib.request
import json
from bs4 import BeautifulSoup
from typing import List, Tuple, Dict, Any
import hashlib

from models.database import WebMonitorModel
from config.config import config


class WebMonitorService:
    """Web监控服务"""
    
    def __init__(self):
        self.db = WebMonitorModel()
        self.lark_webhook_url = config.get_lark_webhook_url()
    
    def monitor_urls(self, urls: List[str] = None):
        """监控多个URL"""
        if urls is None:
            urls = config.get_monitor_urls()
        
        print(f"\n🔍 Monitoring {len(urls)} URLs\n")
        
        changes = []
        
        for url in urls:
            print(f"Checking: {url}")
            url_changes = self._check_url(url)
            if url_changes:
                changes.extend(url_changes)
        
        # 发送通知
        if changes and self.lark_webhook_url:
            self._send_lark_notification(changes)
        
        return changes
    
    def _check_url(self, url: str) -> List[Tuple[str, str, str]]:
        """检查单个URL的变更"""
        content = self._get_page_content(url)
        if not content:
            return []
        
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 获取历史记录
        page_data = self.db.get_page_by_url(url)
        
        changes = []
        
        if page_data and page_data['hash'] != content_hash:
            # 检测到变更
            changes = self._detect_changes(
                page_data['content'],
                content,
                url
            )
        
        # 保存当前状态
        self.db.save_page(url, content, content_hash)
        
        return changes
    
    def _get_page_content(self, url: str) -> str:
        """获取页面内容"""
        try:
            if url.startswith('file://'):
                # 本地文件
                file_path = url.replace('file://', '')
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 网络请求
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # 创建SSL上下文，不验证证书
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10, context=context) as response:
                    return response.read().decode('utf-8')
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return ""
    
    def _detect_changes(self, old_content: str, new_content: str, 
                      url: str) -> List[Tuple[str, str, str]]:
        """检测内容变更"""
        import difflib
        
        changes = []
        
        # 解析HTML
        old_soup = BeautifulSoup(old_content, 'html.parser')
        new_soup = BeautifulSoup(new_content, 'html.parser')
        
        # 检测文本变更
        old_texts = [t.strip() for t in old_soup.get_text().split('\n') if t.strip()]
        new_texts = [t.strip() for t in new_soup.get_text().split('\n') if t.strip()]
        
        diff = difflib.unified_diff(old_texts, new_texts, lineterm='')
        
        for line in diff:
            if line.startswith('- ') and len(line) > 2:
                changes.append(('text', 'deleted', line[2:]))
            elif line.startswith('+ ') and len(line) > 2:
                changes.append(('text', 'added', line[2:]))
        
        # 检测元素变更
        old_elements = self._extract_elements(old_soup)
        new_elements = self._extract_elements(new_soup)
        
        for element_type, elements in new_elements.items():
            if element_type in old_elements:
                old_set = set(old_elements[element_type])
                new_set = set(elements)
                
                added = new_set - old_set
                deleted = old_set - new_set
                
                for elem in added:
                    changes.append((element_type, 'added', str(elem)))
                for elem in deleted:
                    changes.append((element_type, 'deleted', str(elem)))
        
        return changes
    
    def _extract_elements(self, soup: BeautifulSoup) -> Dict[str, List[Any]]:
        """提取页面元素"""
        elements = {
            'images': [],
            'scripts': [],
            'styles': [],
            'links': []
        }
        
        # 图片
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src:
                elements['images'].append(src)
        
        # 脚本
        for script in soup.find_all('script'):
            src = script.get('src', '')
            content = script.string
            if src:
                elements['scripts'].append(src)
            elif content:
                elements['scripts'].append(content[:100])
        
        # 样式
        for style in soup.find_all('style'):
            content = style.string
            if content:
                elements['styles'].append(content[:100])
        
        # 链接
        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href:
                elements['links'].append(href)
        
        return elements
    
    def _send_lark_notification(self, changes: List[Tuple[str, str, str]]):
        """发送飞书通知"""
        if not self.lark_webhook_url:
            return False
        
        # 构建消息
        message = "## Web Page Change Notification\n\n"
        message += f"**Detection Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for element_type, change_type, change_content in changes:
            if element_type == 'text' and change_type == 'modified':
                modified_content = change_content.replace('- ', 'Old content: ').replace('+ ', 'New content: ')
                message += f"### Text Changes\n```\n{modified_content}\n```\n\n"
            else:
                message += f"### {element_type} Changes\n```\n{change_content}\n```\n\n"
        
        # 构建飞书消息格式
        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "title": {
                        "tag": "plain_text",
                        "content": "Web Page Change Notification"
                    },
                    "template": "red"
                },
                "elements": [
                    {
                        "tag": "div",
                        "text": {
                            "tag": "lark_md",
                            "content": message
                        }
                    }
                ]
            }
        }
        
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(
                self.lark_webhook_url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=10, context=context) as response:
                response_data = response.read().decode('utf-8')
                print(f"Lark notification sent successfully: {response_data}")
                return True
        except Exception as e:
            print(f"Failed to send Lark notification: {e}")
            return False