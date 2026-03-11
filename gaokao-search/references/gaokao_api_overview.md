# references/gaokao_api_overview.md

# 阳光高考平台 API 概述

## 基础信息

- **官网**: https://gaokao.chsi.com.cn/
- **备案号**: 教育部学生司主办

## 主要功能页面

| 功能 | URL模式 |
|------|---------|
| 专业检索 | `/zyk/zybk/specialityesByZymcPage?zymc={专业名}` |
| 开设院校 | `/zyk/zybk/ksyxPage?specId={专业ID}` |
| 院校详情 | `/sch/schoolInfoMain--schId-{学校ID}.dhtml` |
| 分数线 | `/zysx/scoreQuery?schId={学校ID}` |
| 招生计划 | `/zyk/zyfl/zsfsPage?yxmc={院校名称}` |

## 反爬建议

1. **请求频率**: 每次请求间隔 2-5 秒随机延迟
2. **User-Agent**: 使用真实浏览器 UA
3. **Cookie**: 首次访问会设置 Cookie，建议保持会话
4. **IP限制**: 高频访问可能触发验证码，建议使用代理池
5. **JavaScript**: 部分数据通过 JS 动态加载，需使用无头浏览器

## 页面结构说明

### 院校列表页

```html
<!-- 典型结构 -->
<table class="zsdx-list">
  <tr>
    <td><a href="/sch/schoolInfoMain--schId-12345.dhtml">学校名称</a></td>
    <td>学校代码</td>
    <td><a href="查看">查看</a></td>
  </tr>
</table>
