# scripts/search_gaokao.py
"""阳光高考平台专业搜索 - 强化反爬版本"""
import json
import re
import os
import time
import random
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import quote, urljoin, urlparse, parse_qs

# ---- Custom exception for 412 handling ----
class PreconditionFailed(Exception):
    """Raised when the target site returns HTTP 412, indicating that a browser‑based fallback is needed."""
    pass

import sys
sys.path.insert(0, str(Path(__file__).parent))

from utils import (
    StealthPlaywright,
    AntiCrawlConfig,
    CaptchaHandler,
    RequestUtils,
    DataExporter,
    load_school_nature
)


class GaokaoSearcher:
    """阳光高考专业搜索类 - 强化版"""
    
    BASE_URL = "https://gaokao.chsi.com.cn"
    SEARCH_URL_TEMPLATE = "https://gaokao.chsi.com.cn/zyk/zybk/specialityesByZymcPage?zymc={major}"
    
    # 反爬状态码
    CAPTCHA_STATUS = [401, 403, 405, 500, 502, 503]
    
    def __init__(self, province: str, major: str, config: AntiCrawlConfig = None):
        self.province = province
        self.major = major
        self.config = config or AntiCrawlConfig()
        self.school_nature = load_school_nature()
        self.results = []
        self.captcha_count = 0
        self.max_captcha_retries = 2
        
    def search(self, max_schools: int = 50) -> List[Dict[str, Any]]:
        """执行搜索主流程"""
        print(f"\n{'='*60}")
        print(f"开始搜索: 省份={self.province}, 专业={self.major}")
        print(f"{'='*60}")
        
        # 尝试多次搜索（处理反爬）
        for attempt in range(1, self.config.max_retries + 1):
            print(f"\n--- 尝试第 {attempt} 次搜索 ---")
            
            try:
                with StealthPlaywright(self.config) as p:
                    # 1. 先访问首页建立会话
                    self._visit_homepage(p)
                    
                    # 2. 搜索专业对应的院校列表
                    schools = self._search_schools(p, max_schools)
                    
                    if not schools:
                        print("阳光高考平台未返回结果")
                        continue
                    
                    print(f"找到 {len(schools)} 所开设 {self.major} 专业的高校")
                    
                    # 3. 获取每所高校的详细招生信息
                    for i, school in enumerate(schools):
                        print(f"\n[{i+1}/{len(schools)}] 处理: {school['name']}")
                        try:
                            detail = self._get_school_detail(p, school)
                            self.results.append(detail)
                        except Exception as e:
                            print(f"  获取信息失败: {e}")
                            self.results.append({
                                'name': school['name'],
                                'code': school.get('code', ''),
                                'nature': self._get_school_nature(school['name']),
                                'enrollment_link': school.get('link', ''),
                                'history': []
                            })
                        
                        # 每处理5所学校后重新访问首页刷新session
                        if (i + 1) % 5 == 0:
                            print("  刷新会话...")
                            p.goto(self.BASE_URL, wait_until="networkidle")
                            RequestUtils.random_delay(2, 4)
                    
                    # 成功获取数据，跳出循环
                    break
                    
            except Exception as e:
                print(f"搜索过程出错: {e}")
                import traceback
                traceback.print_exc()
                
                # 处理 412 预检失败的专门情况，走浏览器插件 fallback
                if isinstance(e, PreconditionFailed):
                    print("⚠️ 触发浏览器插件 fallback（Chrome 扩展）")
                    # 返回特殊标记让外层知道需要手动浏览器介入
                    self.results = None
                    raise e
                
                # 检查是否是验证码问题或已达到重试上限
                if "captcha" in str(e).lower() or self.captcha_count >= self.max_captcha_retries:
                    print("遇到验证码拦截或重试次数已达上限，直接退出...")
                    break
                
                # 等待后重试
                wait_time = self.config.retry_delay * attempt
                print(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
        
        return self.results
    
    def _visit_homepage(self, p: StealthPlaywright):
        """访问首页建立会话"""
        print(f"访问首页: {self.BASE_URL}")
        response = p.goto(self.BASE_URL, wait_until="networkidle")
        # 检查 412 状态码，若出现则抛出自定义异常供外层捕获并走浏览器插件 fallback
        if response and getattr(response, 'status', None) == 412:
            print("⚠️ 遇到 412 Precondition Failed，准备使用浏览器插件 fallback")
            raise PreconditionFailed("首页返回 412")
        
        # 显示首页内容的前500个字符，用于调试
        homepage_content = p.get_content()
        print(f"首页内容前 500 字符: {homepage_content[:500]}...")
        
        # 检查是否有验证码
        if CaptchaHandler.detect_captcha(p.page):
            print("⚠️ 首页出现验证码，尝试处理...")
            if not CaptchaHandler.handle_slider_captcha(p.page):
                self.captcha_count += 1
                raise Exception("需要验证码")
        
        # 随机滚动
        p.scroll_down(random.randint(1, 3))
        
        # 获取并保存 cookies
        cookies = p.context.cookies()
        print(f"已保存 {len(cookies)} 个 cookies")
    
    def _search_schools(self, p: StealthPlaywright, max_schools: int) -> List[Dict[str, Any]]:
        """搜索开设目标专业的高校"""
        # 使用正确的搜索URL
        search_url = self.SEARCH_URL_TEMPLATE.format(major=quote(self.major))
        print(f"搜索URL: {search_url}")
        
        response = p.goto(search_url, wait_until="networkidle")
        if response and getattr(response, 'status', None) == 412:
            print("⚠️ 搜索页面返回 412，准备使用浏览器插件 fallback")
            raise PreconditionFailed("搜索页面返回 412")
        
        # 检查验证码
        if CaptchaHandler.detect_captcha(p.page):
            print("⚠️ 搜索页面出现验证码")
            self.captcha_count += 1
            raise Exception("搜索页面需要验证码")
        
        # 等待页面加载
        time.sleep(2)
        
        # 解析页面，找到专业ID链接
        html = p.get_content()
        
        # 显示页面内容的前500个字符，用于调试
        print(f"页面内容前 500 字符: {html[:500]}...")
        
        # 保存页面内容到文件，用于调试
        with open("search_result.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("搜索结果页面已保存到 search_result.html")
        
        # 查找包含specId的链接
        spec_id_url = self._find_spec_id_link(html)
        if not spec_id_url:
            print("未找到专业ID链接")
            return []
        
        print(f"找到专业ID链接: {spec_id_url}")
        
        # 访问专业ID对应的院校列表页面
        response = p.goto(spec_id_url, wait_until="networkidle")
        if response and getattr(response, 'status', None) == 412:
            print("⚠️ 院校列表页面返回 412，准备使用浏览器插件 fallback")
            raise PreconditionFailed("院校列表返回 412")
        
        # 等待页面加载
        time.sleep(2)
        
        # 保存院校列表页面内容到文件，用于调试
        college_list_html = p.get_content()
        with open("college_list.html", "w", encoding="utf-8") as f:
            f.write(college_list_html)
        print("院校列表页面已保存到 college_list.html")
        
        # 解析院校列表
        schools = self._parse_school_list(college_list_html)
        
        # 如果自动解析失败，尝试其他方式
        if not schools:
            schools = self._parse_by_playwright(p)
        
        # 限制数量
        return schools[:max_schools]
    
    def _find_spec_id_link(self, html: str) -> Optional[str]:
        """查找包含specId的链接"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找所有链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                if '/zyk/zybk/ksyxPage?specId=' in href:
                    return urljoin(self.BASE_URL, href)
            
            return None
        except ImportError:
            # 使用正则表达式
            pattern = r'<a[^>]*href=["\']([^"\']*zyk/zybk/ksyxPage\?specId=[^"\']*)["\'][^>]*>查看</a>'
            match = re.search(pattern, html)
            if match:
                return urljoin(self.BASE_URL, match.group(1))
            return None
    
    def _parse_school_list(self, html: str) -> List[Dict[str, Any]]:
        """解析HTML获取院校列表"""
        schools = []
        
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # 查找所有链接
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # 匹配院校详情页
                if 'schId' in href or 'schoolInfoMain' in href:
                    if text and len(text) > 1 and not any(skip in text.lower() for skip in ['查看', '更多', '详情', '招生']):
                        # 提取学校代码
                        code = self._extract_school_code(href)
                        schools.append({
                            'name': text,
                            'link': urljoin(self.BASE_URL, href),
                            'code': code
                        })
            
            # 去重
            seen = set()
            unique_schools = []
            for s in schools:
                if s['name'] not in seen and len(s['name']) > 2:
                    seen.add(s['name'])
                    unique_schools.append(s)
            
            return unique_schools
            
        except ImportError:
            # 使用正则表达式
            pattern = r'<a[^>]*href=["\']([^"\']*sch(?:ool)?Id[_-]?(\d+)[^"\']*)["\'][^>]*>([^<]+)</a>'
            matches = re.findall(pattern, html)
            
            for match in matches:
                name = match[2].strip()
                if name and len(name) > 2:
                    schools.append({
                        'name': name,
                        'link': urljoin(self.BASE_URL, match[0]),
                        'code': match[1]
                    })
            
            return schools
    
    def _parse_by_playwright(self, p: StealthPlaywright) -> List[Dict[str, Any]]:
        """使用Playwright直接解析页面"""
        schools = []
        
        try:
            # 尝试查找表格
            rows = p.page.query_selector_all('table tr, .school-list li, .result-item')
            
            for row in rows:
                try:
                    # 提取链接
                    link_elem = row.query_selector('a[href*="schId"], a[href*="schoolInfoMain"]')
                    if link_elem:
                        href = link_elem.get_attribute('href')
                        name = link_elem.text_content()
                        
                        if name and href:
                            schools.append({
                                'name': name.strip(),
                                'link': urljoin(self.BASE_URL, href),
                                'code': self._extract_school_code(href)
                            })
                except:
                    continue
                    
        except Exception as e:
            print(f"Playwright解析失败: {e}")
        
        return schools
    
    def _extract_school_code(self, url: str) -> str:
        """从URL提取学校代码"""
        patterns = [
            r'sch(?:ool)?Id[-_]?(\d+)',
            r'schoolInfoMain.*?(\d+)',
            r'sch(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        return ""
    
    def _get_school_detail(self, p: StealthPlaywright, school: Dict[str, Any]) -> Dict[str, Any]:
        """获取高校详细招生信息"""
        detail = {
            'name': school['name'],
            'code': school.get('code', ''),
            'nature': self._get_school_nature(school['name']),
            'enrollment_link': school.get('link', ''),
            'history': []
        }
        
        school_link = school.get('link')
        if not school_link:
            return detail
        
        try:
            # 访问学校详情页
            p.goto(school_link, wait_until="networkidle")
            time.sleep(random.uniform(1, 2))
            
            # 尝试找分数线页面
            history = self._find_score_page(p, school)
            detail['history'] = history
            
        except Exception as e:
            print(f"  获取详情失败: {e}")
        
        return detail
    
    def _find_score_page(self, p: StealthPlaywright, school: Dict[str, Any]) -> List[Dict[str, Any]]:
        """查找并解析分数线页面"""
        history = []
        
        try:
            # 尝试多种方式找分数线链接
            score_selectors = [
                'a:has-text("分数线")',
                'a:has-text("历年分数线")',
                'a:has-text("录取分数线")',
                'a[href*="score"]',
                'a[href*="fsx"]',
            ]
            
            score_link = None
            for selector in score_selectors:
                try:
                    elements = p.page.query_selector_all(selector)
                    for elem in elements:
                        href = elem.get_attribute('href') or ""
                        if href and ('score' in href.lower() or 'fsx' in href.lower()):
                            score_link = href
                            break
                    if score_link:
                        break
                except:
                    continue
            
            # 访问分数线页面
            if score_link:
                p.goto(score_link, wait_until="networkidle")
                history = self._parse_score_table(p)
            else:
                # 尝试构造分数线URL
                school_code = school.get('code')
                if school_code:
                    # 尝试多种URL模式
                    score_urls = [
                        f"{self.BASE_URL}/zysx/scoreQuery?schId={school_code}",
                        f"{self.BASE_URL}/zyk/zyfl/ksfsPage?schId={school_code}",
                        f"{self.BASE_URL}/sch/score--schId-{school_code}.dhtml",
                    ]
                    for url in score_urls:
                        try:
                            p.goto(url, wait_until="networkidle")
                            history = self._parse_score_table(p)
                            if history:
                                break
                        except:
                            continue
                            
        except Exception as e:
            print(f"  查找分数线失败: {e}")
        
        return history
    
    def _parse_score_table(self, p: StealthPlaywright) -> List[Dict[str, Any]]:
        """解析分数线表格"""
        history = []
        
        try:
            # 等待加载
            time.sleep(1)
            
            html = p.get_content()
            
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # 查找表格
                tables = soup.find_all('table')
                
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows[1:]:  # 跳过表头
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            row_text = [c.get_text(strip=True) for c in cells]
                            
                            # 尝试提取年份
                            year = None
                            for text in row_text:
                                year_match = re.search(r'(202[3-5])', text)
                                if year_match:
                                    year = int(year_match.group(1))
                                    break
                            
                            if year:
                                # 提取分数
                                score = None
                                enrollment = None
                                
                                for text in row_text:
                                    # 分数
                                    score_match = re.search(r'(\d+)\s*分', text)
                                    if score_match:
                                        score = int(score_match.group(1))
                                    
                                    # 招生人数
                                    enroll_match = re.search(r'(\d+)\s*[人名]', text)
                                    if enroll_match:
                                        enrollment = int(enroll_match.group(1))
                                
                                if score:
                                    history.append({
                                        'year': year,
                                        'score': score,
                                        'enrollment': enrollment
                                    })
                
                # 去重并排序
                if history:
                    seen = set()
                    unique_history = []
                    for h in history:
                        key = (h['year'], h['score'])
                        if key not in seen:
                            seen.add(key)
                            unique_history.append(h)
                    history = sorted(unique_history, key=lambda x: x['year'], reverse=True)
                    
            except ImportError:
                # 正则解析
                for year in [2025, 2024, 2023]:
                    pattern = rf'{year}[年\s]*(?:理工|文史|综合)?.*?(\d+)\s*分'
                    match = re.search(pattern, html)
                    if match:
                        history.append({
                            'year': year,
                            'score': int(match.group(1)),
                            'enrollment': None
                        })
                        
        except Exception as e:
            print(f"  解析分数线失败: {e}")
        
        return history
    
    def _get_school_nature(self, school_name: str) -> str:
        """获取学校性质"""
        if school_name in self.school_nature:
            return self.school_nature[school_name]['nature']
        
        for known_name, info in self.school_nature.items():
            if known_name in school_name or school_name in known_name:
                return info['nature']
        
        return "其他"
    
    def format_results(self) -> str:
        """格式化结果为Markdown"""
        if not self.results:
            return f"未找到开设 {self.major} 专业的高校信息"
        
        headers = [
            '学校名称', '学校性质', '招生链接',
            '2025招生人数', '2025分数线',
            '2024招生人数', '2024分数线',
            '2023招生人数', '2023分数线'
        ]
        
        rows = []
        for school in self.results:
            history = school.get('history', [])
            history_dict = {h['year']: h for h in history}
            
            row = {
                '学校名称': school['name'],
                '学校性质': school.get('nature', '其他'),
                '招生链接': f"[阳光高考]({school.get('enrollment_link', '')})" if school.get('enrollment_link') else "-",
                '2025招生人数': history_dict.get(2025, {}).get('enrollment', '-'),
                '2025分数线': history_dict.get(2025, {}).get('score', '-'),
                '2024招生人数': history_dict.get(2024, {}).get('enrollment', '-'),
                '2024分数线': history_dict.get(2024, {}).get('score', '-'),
                '2023招生人数': history_dict.get(2023, {}).get('enrollment', '-'),
                '2023分数线': history_dict.get(2023, {}).get('score', '-'),
            }
            rows.append(row)
        
        return DataExporter.to_markdown_table(rows, headers)


def search_gaokao(province: str, major: str, output_file: str = None) -> str:
    """主搜索函数"""
    # 配置反爬参数
    config = AntiCrawlConfig(
        min_delay=3.0,      # 最小延迟3秒
        max_delay=8.0,      # 最大延迟8秒
        headless=True,
        enable_stealth=True,
        max_retries=3,
        retry_delay=10.0,   # 重试间隔10秒
    )
    
    searcher = GaokaoSearcher(province, major, config)
    try:
        results = searcher.search()
    except PreconditionFailed as pf:
        # 触发浏览器插件 fallback：返回特殊标记，外层可据此打开 Chrome
        print(f"⚠️ 触发浏览器插件 fallback: {pf}")
        return f"__BROWSER_FALLBACK__|{searcher.province}|{searcher.major}"
    
    output = searcher.format_results()
    output += "\n\n> 数据来源：阳光高考平台（https://gaokao.chsi.com.cn）及高校官方网站。\n"
    
    if output_file:
        DataExporter.save_to_file(output, output_file)
        print(f"结果已保存到: {output_file}")
    
    return output


if __name__ == "__main__":
    result = search_gaokao("浙江", "软件工程")
    print(result)
