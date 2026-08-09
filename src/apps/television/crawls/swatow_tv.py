"""“今日视线”节目采集器。

采集器只保存节目元数据和源站可播放地址，不下载、合并或重新分发节目视频文件。
这样既让网页与客户端能够直接播放，也让每条内容始终可回溯到原始发布页面。
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime, time
from typing import Iterable, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.db import transaction
from django.utils import timezone
from loguru import logger
from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from apps.television.models import TvProgram, Video


# 源站地址集中定义，便于源站改版时只调整此处，而不用修改任务或 API 代码。
# 源站发生域名或栏目迁移时可由部署环境覆盖，无需发版修改爬虫。
# 旧 dahuawang.com 域名已经迁移；当前栏目保留在同一内容结构的新站域名。
SOURCE_ROOT = os.environ.get('TODAY_TV_SOURCE_ROOT', 'https://strtv.strtv.cn').rstrip('/')
SOURCE_LISTING_URL = os.environ.get(
    'TODAY_TV_LISTING_URL',
    f'{SOURCE_ROOT}/b/a/list_dahua.shtml',
)
PROGRAM_NAME = '今日视线'
DATE_PATTERN = re.compile(r'(20\d{2})[-年/.](\d{1,2})[-月/.](\d{1,2})')


class CrawlError(RuntimeError):
    """源站不可访问或页面结构无法解析时抛出，供任务更新节目状态。"""


@dataclass(frozen=True)
class SourceVideo:
    """从源站解析出的一条节目片段；字段保持为原始来源的可追溯信息。"""

    title: str
    published_date: date
    detail_url: str
    cover_url: Optional[str] = None
    playback_url: Optional[str] = None

    @property
    def source_key(self) -> str:
        """用稳定的详情页地址生成数据库唯一键，而不是容易重复的节目标题。"""
        return hashlib.sha256(self.detail_url.encode('utf-8')).hexdigest()

    def as_dict(self) -> dict:
        """将日期序列化为日志和命令行输出都易读的 ISO 格式。"""
        data = asdict(self)
        data['published_date'] = self.published_date.isoformat()
        return data


def extract_date(text: str) -> Optional[date]:
    """从“今日视线 2026-08-09”等标题中兼容解析常见日期格式。"""
    match = DATE_PATTERN.search(text or '')
    if not match:
        return None
    try:
        return date(*(int(part) for part in match.groups()))
    except ValueError:
        # 源站偶发录入错误时跳过坏数据，不能让整个同步任务中断。
        return None


def clean_title(title: str) -> str:
    """移除日期和多余分隔符，保留在用户界面中可读的节目标题。"""
    title_without_date = DATE_PATTERN.sub('', title or '')
    return re.sub(r'^[\s\-—_|【】\[\]()（）]+|[\s\-—_|【】\[\]()（）]+$', '', title_without_date)


class TodayTVCrawler:
    """面向源站当前 HTML 结构的容错采集器。"""

    def __init__(self, session: Optional[Session] = None, timeout_seconds: int = 20):
        self.timeout_seconds = timeout_seconds
        self.session = session or self._build_session()

    @staticmethod
    def _build_session() -> Session:
        """为临时网络错误配置有限重试，避免定时任务因单次抖动失败。"""
        session = Session()
        retry = Retry(
            total=3,
            backoff_factor=0.6,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({'GET'}),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('https://', adapter)
        session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'TodayTV/1.0 (+metadata synchronizer)',
        })
        return session

    @staticmethod
    def listing_url(page_number: int) -> str:
        """返回源站的列表分页地址；第一页与后续页面的规则并不相同。"""
        if page_number < 1:
            raise ValueError('page_number 必须大于等于 1')
        if page_number == 1:
            return SOURCE_LISTING_URL
        return f'{SOURCE_ROOT}/b/a/list_more_dahua_{page_number}.html'

    def _get_html(self, url: str) -> str:
        """请求并验证 HTML 响应，集中处理网络和解码错误。"""
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            response.raise_for_status()
        except Exception as exc:  # requests 会抛出多个具体异常，统一转为领域错误。
            raise CrawlError(f'请求源站失败：{url}') from exc

        # 源站有时把 UTF-8 页面错误标成 ISO-8859-1。优先页面自身声明和 UTF-8，
        # 最后才回退 GB18030，避免中文标题乱码导致日期正则无法匹配。
        raw_html = response.content
        charset_match = re.search(
            br'<meta[^>]+charset=["\']?([a-zA-Z0-9_-]+)', raw_html[:4096], re.IGNORECASE,
        )
        declared_encoding = charset_match.group(1).decode('ascii') if charset_match else None
        # 实测该页面会把 UTF-8 内容误标成 ISO-8859-1；Latin-1 永远能“成功”解码，
        # 所以只能作为最后保底，不能抢在 UTF-8 之前。
        candidates = [
            'utf-8',
            declared_encoding if declared_encoding and declared_encoding.lower() not in {'iso-8859-1', 'latin-1'} else None,
            'gb18030',
            response.encoding if response.encoding and response.encoding.lower() not in {'iso-8859-1', 'latin-1'} else None,
            declared_encoding,
            response.encoding,
        ]
        for encoding in dict.fromkeys(value for value in candidates if value):
            try:
                return raw_html.decode(encoding)
            except (LookupError, UnicodeDecodeError):
                continue
        # 极少数异常页面仍保留可读内容，供错误日志和后续选择器排障。
        return raw_html.decode('utf-8', errors='replace')

    @staticmethod
    def _first_attr(element, selectors: Iterable[str], attributes: Iterable[str]) -> Optional[str]:
        """从多个可能的节点及属性中取第一个非空地址，兼容小范围模板调整。"""
        for selector in selectors:
            node = element.select_one(selector)
            if not node:
                continue
            for attribute in attributes:
                value = node.get(attribute)
                if value:
                    return value.strip()
        return None

    def parse_listing(self, html: str, listing_url: str) -> list[SourceVideo]:
        """解析一个节目列表页，先得到详情页和封面，播放地址在下一步解析。"""
        soup = BeautifulSoup(html, 'html.parser')
        fragments: list[SourceVideo] = []
        seen_urls: set[str] = set()

        # news-item 是当前源站结构；li 回退分支让标题和链接仍可被温和地发现。
        candidates = soup.select('li.news-item, .news-item') or soup.find_all('li')
        for item in candidates:
            # 选择器合并会按 DOM 顺序返回封面 a 标签；这里必须逐一尝试，
            # 让含标题的节点优先于只有图片的详情链接。
            anchor = None
            for selector in ('.text-box .tit a', '.tit a', 'h1 a', 'h2 a', 'h3 a', 'a[href]'):
                candidate = item.select_one(selector)
                if candidate and candidate.get_text(' ', strip=True):
                    anchor = candidate
                    break
            if not anchor:
                continue
            raw_title = anchor.get_text(' ', strip=True)
            published_date = extract_date(raw_title)
            detail_href = anchor.get('href')
            # 没有日期的导航和广告链接不是节目内容，直接过滤掉。
            if not raw_title or not published_date or not detail_href:
                continue

            detail_url = urljoin(listing_url, detail_href)
            if detail_url in seen_urls:
                continue
            seen_urls.add(detail_url)
            cover_href = self._first_attr(item, ('img',), ('data-src', 'data-original', 'src'))
            cover_url = urljoin(listing_url, cover_href) if cover_href else None
            fragments.append(SourceVideo(
                title=clean_title(raw_title) or PROGRAM_NAME,
                published_date=published_date,
                detail_url=detail_url,
                cover_url=cover_url,
            ))
        return fragments

    def parse_detail(self, fragment: SourceVideo, html: str) -> SourceVideo:
        """从详情页提取标准 video/source 地址，并在必要时补全封面。"""
        soup = BeautifulSoup(html, 'html.parser')
        playback_href = self._first_attr(
            soup,
            ('video', 'video source', 'source[type^="video/"]'),
            ('src', 'data-src', 'data-original'),
        )
        if not playback_href:
            # 部分页面把播放器地址放在 Open Graph 标签中，作为最后一个保守回退。
            meta = soup.select_one('meta[property="og:video"], meta[property="og:video:url"]')
            playback_href = meta.get('content') if meta else None

        cover_url = fragment.cover_url
        if not cover_url:
            meta_cover = soup.select_one('meta[property="og:image"]')
            if meta_cover and meta_cover.get('content'):
                cover_url = urljoin(fragment.detail_url, meta_cover['content'])

        return SourceVideo(
            title=fragment.title,
            published_date=fragment.published_date,
            detail_url=fragment.detail_url,
            cover_url=cover_url,
            playback_url=urljoin(fragment.detail_url, playback_href) if playback_href else None,
        )

    def crawl(self, pages: int = 3) -> list[SourceVideo]:
        """采集最近若干列表页并去重；无法播放的条目不写入数据库。"""
        if not 1 <= pages <= 20:
            raise ValueError('pages 必须在 1 到 20 之间')

        discovered: dict[str, SourceVideo] = {}
        for page_number in range(1, pages + 1):
            page_url = self.listing_url(page_number)
            for fragment in self.parse_listing(self._get_html(page_url), page_url):
                discovered.setdefault(fragment.detail_url, fragment)

        videos: list[SourceVideo] = []
        for fragment in discovered.values():
            parsed = self.parse_detail(fragment, self._get_html(fragment.detail_url))
            if parsed.playback_url:
                videos.append(parsed)
            else:
                logger.warning('跳过没有可播放地址的节目：{}', fragment.detail_url)
        return videos

    def sync(self, pages: int = 3) -> dict[str, int | str]:
        """将最新采集结果以幂等方式写入数据库，并同步节目状态和时间戳。"""
        program, _ = TvProgram.objects.get_or_create(
            name=PROGRAM_NAME,
            defaults={'source_url': SOURCE_LISTING_URL},
        )
        program.status = TvProgram.Status.SCRAPING
        program.source_url = SOURCE_LISTING_URL
        program.last_synced_time = timezone.now()
        program.save(update_fields=['status', 'source_url', 'last_synced_time', 'updated_time'])

        created_count = 0
        updated_count = 0
        try:
            source_videos = self.crawl(pages=pages)
            with transaction.atomic():
                for source_video in source_videos:
                    # source_key 保证任务重试、分页重叠和人工重复执行都不会产生重复节目。
                    _, created = Video.objects.update_or_create(
                        source_key=source_video.source_key,
                        defaults={
                            'program': program,
                            'name': source_video.title,
                            'time': datetime.combine(source_video.published_date, time.min),
                            'related_link': source_video.detail_url,
                            'origin_link': source_video.playback_url,
                            'cover_link': source_video.cover_url,
                            'video_link': source_video.playback_url,
                        },
                    )
                    created_count += int(created)
                    updated_count += int(not created)

                newest_date = max((item.published_date for item in source_videos), default=None)
                program.status = TvProgram.Status.UPDATED
                program.local_update_time = timezone.now()
                if newest_date:
                    program.first_detected_update_time = datetime.combine(newest_date, time.min)
                program.save(update_fields=[
                    'status', 'first_detected_update_time', 'local_update_time', 'updated_time',
                ])
        except Exception:
            # 失败状态会直接展示在管理后台和产品页，便于维护者察觉源站变更。
            program.status = TvProgram.Status.FAILED
            program.save(update_fields=['status', 'updated_time'])
            raise

        logger.info('今日视线同步完成：新增 {} 条，更新 {} 条', created_count, updated_count)
        return {
            'program': program.name,
            'created': created_count,
            'updated': updated_count,
            'total': created_count + updated_count,
        }
