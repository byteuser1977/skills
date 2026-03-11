import requests
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
from utils import RequestUtils

# 测试链接
url = "https://gaokao.chsi.com.cn/zyk/zybk/ksyxPage?specId=73384828"

print(f"测试访问: {url}")

# 设置请求头
headers = RequestUtils.DEFAULT_HEADERS

# 发送请求
try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    print(f"页面内容长度: {len(response.text)} 字符")
    print(f"页面内容前 500 字符: {response.text[:500]}...")
except Exception as e:
    print(f"请求失败: {e}")
