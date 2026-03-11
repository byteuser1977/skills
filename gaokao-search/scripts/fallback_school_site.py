# scripts/fallback_school_site.py
"""
兜底抓取模块 - 当阳光高考平台无数据时，访问高校官网获取招生信息
"""

import re
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import random

try:
    import requests
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: requests or BeautifulSoup not installed")

# 导入工具模块
import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils import RequestUtils


class SchoolSiteScraper:
    """高校官网招生信息抓取类"""
    
    # 常见招生页面URL模式
    ADMISSION_PATTERNS = [
        "/zsxx/",
        "/zs/",
        "/zhaosheng/",
        "/招生信息/",
        "/招生网/",
        "/zsw/",
        "/gaokao/",
        "/bkzs/",
        "/lqxx/",
        "/录取信息/",
    ]
    
    # 常见招生网站域名
    COMMON_ADMISSION_DOMAINS = [
        "zsw.",
        "zs.",
        "zhaosheng.",
        "gaokao.",
        "bkzs.",
    ]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(RequestUtils.DEFAULT_HEADERS)
    
    def search_school_admission(self, school_name: str) -> Dict[str, Any]:
        """
        搜索高校招生信息
        
        Args:
            school_name: 学校名称
        
        Returns:
            包含招生信息的字典
        """
        print(f"  正在搜索 {school_name} 的招生信息...")
        
        result = {
            'school_name': school_name,
            'admission_url': None,
            'history': [],
            'source': '高校官网'
        }
        
        # 1. 尝试构造招生页面URL
        admission_url = self._construct_admission_url(school_name)
        
        if admission_url:
            result['admission_url'] = admission_url
            result['history'] = self._scrape_admission_page(admission_url)
        
        # 2. 如果构造失败，尝试搜索引擎
        if not result['history']:
            search_url = self._get_search_url(school_name)
            result['admission_url'] = search_url
            result['history'] = self._scrape_search_results(search_url)
        
        return result
    
    def _construct_admission_url(self, school_name: str) -> Optional[str]:
        """构造可能的招生页面URL"""
        
        # 移除常见后缀
        clean_name = school_name.replace("大学", "").replace("学院", "").strip()
        
        # 常见域名模式
        domains = [
            f"https://www.{clean_name}.edu.cn",
            f"https://zsw.{clean_name}.edu.cn",
            f"https://zs.{clean_name}.edu.cn",
            f"https://{clean_name}.edu.cn",
        ]
        
        for domain in domains:
            for pattern in self.ADMISSION_PATTERNS:
                url = domain + pattern
                if self._check_url_exists(url):
                    return url
        
        return None
    
    def _check_url_exists(self, url: str) -> bool:
        """检查URL是否存在"""
        try:
            response = self.session.head(url, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False
    
    def _get_search_url(self, school_name: str) -> str:
        """获取搜索引擎URL"""
        # 使用百度搜索招生信息
        query = f"{school_name} 招生信息 分数线"
        encoded_query = RequestUtils.clean_text(query).replace(" ", "+")
        return f"https://www.baidu.com/s?wd={encoded_query}&pn=0"
    
    def _scrape_admission_page(self, url: str) -> List[Dict[str, Any]]:
        """抓取招生页面内容"""
        history = []
        
        try:
            RequestUtils.random_delay(1, 2)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            
            # 提取分数线信息
            years = [2025, 2024, 2023]
            for year in years:
                # 分数线模式
                score_patterns = [
                    rf'{year}[年\s]*.*?(?:理工|文史|综合|物理|历史)[类\s]*(?:一批|二批)?.*?(\d+)\s*分',
                    rf'{year}\s*年.*?分数线[：:]\s*(\d+)',
                    rf'分数线[：:]\s*{year}.*?(\d+)',
                ]
                
                for pattern in score_patterns:
                    match = re.search(pattern, text)
                    if match:
                        history.append({
                            'year': year,
                            'score': int(match.group(1)),
                            'enrollment': None
                        })
                        break
            
            # 提取招生人数
            enrollment_patterns = [
                rf'(\d+)\s*人',
                rf'招生.*?(\d+)\s*名',
                rf'计划.*?(\d+)\s*人',
            ]
            
            for pattern in enrollment_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    # 尝试匹配到对应年份
                    for i, h in enumerate(history):
                        if h.get('enrollment') is None and i < len(matches):
                            try:
                                h['enrollment'] = int(matches[i])
                            except:
                                pass
        
        except Exception as e:
            print(f"    抓取失败: {e}")
        
        return history
    
    def _scrape_search_results(self, search_url: str) -> List[Dict[str, Any]]:
        """从搜索引擎结果页面抓取"""
        history = []
        
        try:
            RequestUtils.random_delay(1, 2)
            response = self.session.get(search_url, timeout=30)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找招生信息链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text()
                
                # 查找看起来像招生页面的链接
                if any(pattern in text.lower() for pattern in ['招生', '分数线', '录取']):
                    try:
                        # 追踪重定向获取真实URL
                        real_url = self.session.resolve_redirects(
                            self.session.get(href, timeout=10, allow_redirects=True),
                            href
                        )[0].url if href.startswith('http') else href
                        
                        # 抓取该页面
                        page_history = self._scrape_admission_page(real_url)
                        if page_history:
                            history.extend(page_history)
                            break
                    except:
                        continue
        
        except Exception as e:
            print(f"    搜索引擎抓取失败: {e}")
        
        return history


def fallback_scrape(school_name: str) -> Dict[str, Any]:
    """
    兜底抓取函数
    
    Args:
        school_name: 学校名称
    
    Returns:
        招生信息字典
    """
    scraper = SchoolSiteScraper()
    return scraper.search_school_admission(school_name)


if __name__ == "__main__":
    # 测试
    result = fallback_scrape("浙江大学")
    print(json.dumps(result, ensure_ascii=False, indent=2))
