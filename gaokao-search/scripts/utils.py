# scripts/utils.py
"""通用工具模块 - 强化反反爬版本"""
import random
import time
import json
import re
import hashlib
from typing import Optional, Dict, List, Any
from pathlib import Path
from dataclasses import dataclass, field

try:
    from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed")


# ============ 配置类 ============
@dataclass
class AntiCrawlConfig:
    """反爬配置"""
    # 延迟配置
    min_delay: float = 3.0      # 最小延迟（秒）
    max_delay: float = 8.0      # 最大延迟（秒）
    
    # 浏览器配置
    headless: bool = True
    disable_images: bool = True  # 禁用图片加速
    slow_mo: int = 100           # 模拟操作延迟
    
    # 反检测配置
    enable_stealth: bool = True
    random_viewport: bool = True
    
    # 重试配置
    max_retries: int = 3
    retry_delay: float = 5.0
    
    # 代理配置
    proxy_server: str = ""      # 代理服务器，如 "http://ip:port"
    proxy_username: str = ""
    proxy_password: str = ""


# ============ 真实浏览器指纹 ============
class BrowserFingerprints:
    """浏览器指纹库"""
    
    WINDOWS_UA = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
    ]
    
    MAC_UA = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ]
    
    VIEWPORTS = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1440, 'height': 900},
        {'width': 1536, 'height': 864},
        {'width': 1280, 'height': 720},
    ]
    
    @classmethod
    def random_ua(cls, os_type: str = 'windows') -> str:
        if os_type.lower() == 'mac':
            return random.choice(cls.MAC_UA)
        return random.choice(cls.WINDOWS_UA)
    
    @classmethod
    def random_viewport(cls) -> Dict[str, int]:
        return random.choice(cls.VIEWPORTS)


# ============ 核心工具类 ============
class RequestUtils:
    """增强版请求工具"""
    
    # 默认请求头
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    @staticmethod
    def random_delay(min_sec: float = 3.0, max_sec: float = 8.0) -> float:
        """随机延迟"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return delay
    
    @staticmethod
    def random_jitter() -> float:
        """微抖动延迟（0.1-0.5秒）"""
        return random.uniform(0.1, 0.5)
    
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def parse_score_line(score_text: str) -> Optional[Dict[str, Any]]:
        if not score_text:
            return None
        patterns = [
            r'(\d{4})年\s*(理工类|文史类|综合|物理类|历史类)?\s*(本科一批|本科二批|专科批|提前批)?\s*(\d+)\s*分',
            r'(\d{4})\s*年\s*(\d+)\s*分',
        ]
        for pattern in patterns:
            match = re.search(pattern, score_text)
            if match:
                result = {'year': int(match.group(1)), 'score': int(match.group(-1))}
                if len(match.groups()) >= 2:
                    result['category'] = match.group(2)
                if len(match.groups()) >= 3:
                    result['batch'] = match.group(3)
                return result
        return None


# ============ 强化版Playwright工具 ============
class StealthPlaywright:
    """强化反检测的Playwright包装器"""
    
    def __init__(self, config: AntiCrawlConfig = None):
        self.config = config or AntiCrawlConfig()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.request_count = 0
        self.last_request_time = 0
        
    def __enter__(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not available")
        
        self.playwright = sync_playwright().start()
        
        # 浏览器启动参数
        launch_options = {
            'headless': self.config.headless,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        }
        
        # 代理配置
        if self.config.proxy_server:
            launch_options['proxy'] = {
                'server': self.config.proxy_server,
                'username': self.config.proxy_username if self.config.proxy_username else None,
                'password': self.config.proxy_password if self.config.proxy_password else None,
            }
        
        self.browser = self.playwright.chromium.launch(**launch_options)
        
        # 创建上下文
        context_options = self._get_context_options()
        self.context = self.browser.new_context(**context_options)
        
        # 禁用图片（加速）
        if self.config.disable_images:
            self.context.route("**/*.{png,jpg,jpeg,gif,ico,svg,webp}", lambda route: route.abort())
        
        self.page = self.context.new_page()
        
        # 注入反检测脚本
        if self.config.enable_stealth:
            self._inject_stealth_scripts()
        
        # 设置请求拦截
        self._setup_request_interceptor()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup()
    
    def _get_context_options(self) -> Dict[str, Any]:
        """获取上下文配置"""
        ua = BrowserFingerprints.random_ua()
        viewport = BrowserFingerprints.random_viewport() if self.config.random_viewport else {'width': 1920, 'height': 1080}
        
        options = {
            'user_agent': ua,
            'viewport': viewport,
            'locale': 'zh-CN',
            'timezone_id': 'Asia/Shanghai',
            'geolocation': {'latitude': 30.2741, 'longitude': 120.1551},  # 杭州
            'permissions': ['geolocation'],
            'extra_http_headers': {
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        }
        
        return options
    
    def _inject_stealth_scripts(self):
        """注入反检测脚本"""
        stealth_script = """
        // 1. 隐藏 webdriver
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 2. 模拟 Chrome 运行时
        window.chrome = {
            runtime: {},
            app: {
                isInstalled: false
            },
            webstore: {
                onInstallStageChanged: {},
                onDownloadProgress: {}
            }
        };
        
        // 3. 修改 permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 4. 修改 plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
                { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
            ]
        });
        
        // 5. 修改 languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['zh-CN', 'zh', 'en-US', 'en']
        });
        
        // 6. 添加 Chrome 内部属性
        window.navigator.chrome = {
            runtime: {},
            app: {
                isInstalled: false
            },
            webstore: {
                onInstallStageChanged: {},
                onDownloadProgress: {}
            }
        };
        
        // 7. 修改 mimeTypes
        Object.defineProperty(navigator, 'mimeTypes', {
            get: () => [
                { type: 'application/pdf', suffixes: 'pdf', description: 'Adobe Acrobat PDF' },
                { type: 'application/x-google-chrome-pdf', suffixes: 'pdf', description: 'Portable Document Format' },
                { type: 'application/x-nacl', suffixes: '', description: 'Native Client Executable' }
            ]
        });
        
        // 8. 伪造连接信息
        Object.defineProperty(navigator, 'connection', {
            get: () => ({
                effectiveType: '4g',
                rtt: 50,
                downlink: 10,
                saveData: false,
                onchange: null
            })
        });
        
        // 9. 修改 hardwareConcurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8
        });
        
        // 10. 修改 deviceMemory
        Object.defineProperty(navigator, 'deviceMemory', {
            get: () => 8
        });
        
        // 11. 隐藏 Playwright 特征
        Object.defineProperty(navigator, 'userAgent', {
            get: () => navigator.userAgent.replace('HeadlessChrome', 'Chrome')
        });
        
        // 12. 模拟真实的 navigator 对象
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32'
        });
        
        Object.defineProperty(navigator, 'productSub', {
            get: () => '20030107'
        });
        
        Object.defineProperty(navigator, 'vendor', {
            get: () => 'Google Inc.'
        });
        
        Object.defineProperty(navigator, 'maxTouchPoints', {
            get: () => 5
        });
        
        // 13. 模拟真实的 window 对象
        Object.defineProperty(window, 'outerWidth', {
            get: () => window.innerWidth
        });
        
        Object.defineProperty(window, 'outerHeight', {
            get: () => window.innerHeight
        });
        
        // 14. 模拟真实的 document 对象
        Object.defineProperty(document, 'hidden', {
            get: () => false
        });
        
        Object.defineProperty(document, 'visibilityState', {
            get: () => 'visible'
        });
        
        // 15. 模拟真实的 screen 对象
        Object.defineProperty(screen, 'width', {
            get: () => window.innerWidth
        });
        
        Object.defineProperty(screen, 'height', {
            get: () => window.innerHeight
        });
        
        Object.defineProperty(screen, 'colorDepth', {
            get: () => 24
        });
        """
        self.page.add_init_script(stealth_script)
    
    def _setup_request_interceptor(self):
        """设置请求拦截器 - 控制请求频率"""
        def handle_route(route):
            # 请求频率控制
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.config.min_delay:
                sleep_time = self.config.min_delay - time_since_last + random.uniform(0, 1)
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            # 继续请求
            route.continue_()
        
        self.page.route("**/*", handle_route)
    
    def goto(self, url: str, wait_until: str = "networkidle", timeout: int = 60000) -> "StealthPlaywright":
        """导航到URL"""
        try:
            response = self.page.goto(url, wait_until=wait_until, timeout=timeout)
            
            # 检查状态码
            if response and response.status == 412:
                print(f"遇到 412 状态码，直接退出: {url}")
                raise Exception("412 Precondition Failed")
            
            RequestUtils.random_jitter()
        except PlaywrightTimeout:
            print(f"页面加载超时: {url}")
        except Exception as e:
            print(f"导航失败: {e}")
        return self
    
    def wait_for_selector(self, selector: str, timeout: int = 30000):
        """等待元素"""
        try:
            return self.page.wait_for_selector(selector, timeout=timeout)
        except PlaywrightTimeout:
            return None
    
    def click(self, selector: str):
        """模拟人类点击"""
        try:
            # 随机移动到元素位置
            box = self.page.locator(selector).first.bounding_box()
            if box:
                x = box['x'] + box['width'] / 2 + random.randint(-10, 10)
                y = box['y'] + box['height'] / 2 + random.randint(-10, 10)
                self.page.mouse.move(x, y)
                RequestUtils.random_jitter()
            
            self.page.click(selector)
            RequestUtils.random_jitter()
        except Exception as e:
            print(f"点击失败: {e}")
    
    def fill(self, selector: str, value: str):
        """模拟人类输入"""
        try:
            # 逐字符输入
            self.page.click(selector)
            self.page.keyboard.press('Control+a')
            self.page.keyboard.press('Backspace')
            
            for char in value:
                self.page.keyboard.type(char, delay=random.randint(50, 150))
            
            RequestUtils.random_jitter()
        except Exception as e:
            print(f"输入失败: {e}")
    
    def scroll_down(self, times: int = 1):
        """模拟人类滚动"""
        for _ in range(times):
            self.page.mouse.wheel(0, random.randint(300, 600))
            RequestUtils.random_jitter()
    
    def get_content(self) -> str:
        """获取页面内容"""
        return self.page.content()
    
    def _cleanup(self):
        """清理资源"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass


# ============ 验证码处理 ============
class CaptchaHandler:
    """验证码处理"""
    
    @staticmethod
    def detect_captcha(page) -> bool:
        """检测是否出现验证码"""
        # 检查常见验证码元素
        captcha_selectors = [
            '#captcha', 
            '.captcha',
            '#verifycode',
            '.verify-code',
            'input[name="verifyCode"]',
            'img[src*="captcha"]',
            'iframe[src*="captcha"]',
            'div[class*="captcha"]',
            'div[class*="verify"]',
        ]
        
        for selector in captcha_selectors:
            try:
                if page.locator(selector).count() > 0:
                    return True
            except:
                continue
        
        # 检查页面文本
        page_text = page.content().lower()
        captcha_keywords = ['验证码', '验证吗', 'verify code', 'captcha', '安全验证']
        return any(keyword in page_text for keyword in captcha_keywords)
    
    @staticmethod
    def handle_slider_captcha(page) -> bool:
        """处理滑块验证码（需要额外集成打码平台）"""
        print("检测到滑块验证码，需要手动处理或集成打码平台")
        # 这里可以集成第三方打码服务
        # 如 超级鹰、打码兔等
        return False


# ============ 数据导出 ============
class DataExporter:
    @staticmethod
    def to_markdown_table(data: List[Dict[str, Any]], headers: List[str]) -> str:
        if not data:
            return "暂无数据"
        
        header_row = "| " + " | ".join(headers) + " |"
        separator = "| " + " | ".join(["---"] * len(headers)) + " |"
        
        rows = []
        for item in data:
            row = "| " + " | ".join([str(item.get(h, "")) for h in headers]) + " |"
            rows.append(row)
        
        return "\n".join([header_row, separator] + rows)
    
    @staticmethod
    def save_to_file(content: str, filepath: str) -> str:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath


# ============ 高校性质加载 ============
def load_school_nature() -> Dict[str, Dict[str, str]]:
    """加载高校性质对照表"""
    school_nature_file = Path(__file__).parent.parent / "references" / "school_nature.md"
    if not school_nature_file.exists():
        return {}
    
    nature_data = {}
    current_category = None
    
    with open(school_nature_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('## '):
                current_category = line[3:].strip()
            elif line.startswith('- ') or line.startswith('* '):
                school_name = line[2:].strip()
                if school_name and current_category:
                    nature_data[school_name] = {
                        'nature': current_category,
                        'code': get_nature_code(current_category)
                    }
    return nature_data


def get_nature_code(nature: str) -> str:
    mapping = {'985': '985', '211': '211', '双一流': '双一流', '其他': '其他'}
    return mapping.get(nature, '其他')
