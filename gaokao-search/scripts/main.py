# scripts/main.py
"""高考志愿搜索主程序 - 强化反爬版"""
import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from search_gaokao import GaokaoSearcher, search_gaokao
from fallback_school_site import fallback_scrape
from utils import DataExporter, AntiCrawlConfig


def main():
    parser = argparse.ArgumentParser(description='高考志愿搜索工具（强化反爬版）')
    parser.add_argument('--province', '-p', required=True, help='考生所在省份')
    parser.add_argument('--major', '-m', required=True, help='意向专业')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--headless', action='store_true', default=True, help='无头模式')
    parser.add_argument('--fallback', action='store_true', default=True, help='启用兜底抓取')
    parser.add_argument('--max-schools', type=int, default=30, help='最大搜索学校数')
    parser.add_argument('--min-delay', type=float, default=3.0, help='最小请求延迟（秒）')
    parser.add_argument('--max-delay', type=float, default=8.0, help='最大请求延迟（秒）')
    parser.add_argument('--proxy', type=str, help='代理服务器，如 http://ip:port')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("高考志愿搜索工具（强化反爬版）")
    print(f"省份: {args.province}")
    print(f"专业: {args.major}")
    print(f"延迟范围: {args.min_delay}-{args.max_delay}秒")
    if args.proxy:
        print(f"代理: {args.proxy}")
    print("=" * 60)
    
    # 配置
    config = AntiCrawlConfig(
        min_delay=args.min_delay,
        max_delay=args.max_delay,
        headless=args.headless,
        enable_stealth=True,
        max_retries=3,
        retry_delay=10.0,
        proxy_server=args.proxy or "",
    )
    
    # 搜索
    searcher = GaokaoSearcher(args.province, args.major, config)
    results = searcher.search(max_schools=args.max_schools)
    
    # 兜底抓取补充
    if args.fallback:
        print("\n检查并补充缺失数据...")
        for result in results:
            history = result.get('history', [])
            if not history or all(h.get('score') is None for h in history):
                print(f"  补充抓取: {result['name']}")
                try:
                    fallback_result = fallback_scrape(result['name'])
                    if fallback_result.get('history'):
                        result['history'].extend(fallback_result['history'])
                        result['fallback_url'] = fallback_result.get('admission_url', '')
                except Exception as e:
                    print(f"    失败: {e}")
    
    # 输出
    output = searcher.format_results()
    sources = ["阳光高考平台（https://gaokao.chsi.com.cn）"]
    if args.fallback:
        sources.append("高校官方网站")
    output += f"\n\n> 数据来源：{' 及 '.join(sources)}。"
    
    if args.output:
        DataExporter.save_to_file(output, args.output)
        print(f"\n结果已保存到: {args.output}")
    else:
        print("\n" + "=" * 60)
        print("搜索结果:")
        print("=" * 60)
        print(output)


if __name__ == "__main__":
    main()
