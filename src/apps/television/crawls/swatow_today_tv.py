import datetime
import shutil
import re
import os
import uuid
import time
import json
from pprint import pprint
from typing import Optional, List, Dict
from datetime import date, timedelta
from bs4 import BeautifulSoup
from loguru import logger
from requests import Session

from django_starter.contrib.config import services as djs_cfg

DATE_PATTERN = re.compile(r'\d{4}-\d{1,2}-\d{1,2}')

CONFIG = {
    'base_dir': os.path.dirname(os.path.abspath(__file__)),
    # 采集的页面范围
    'crawl_pages': 3,
    'output_dir': r'P:\今日视线',
    'proxy': djs_cfg.get_bool('use_proxy'),
    'proxy_url': djs_cfg.get_str('proxy_url'),
    'use_proxy_pool': djs_cfg.get_bool('use_proxy_pool'),
    'proxy_pool_api_base': djs_cfg.get_str('proxy_pool_api_base'),
}

default_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7,th;q=0.6",
    "Cache-Control": "no-cache", "Dnt": "1", "Pragma": "no-cache", "Priority": "u=0, i",
    "Sec-Ch-Ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
    "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Site": "none", "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

session = Session()
session.headers.update(djs_cfg.get_json('headers'))

if CONFIG['proxy']:
    session.proxies.update({
        'http': CONFIG['proxy_url'],
    })
    if CONFIG['use_proxy_pool']:
        from utilities.proxy_pool import ProxyPool

        proxy_pool = ProxyPool(CONFIG['proxy_pool_api_base'])
        session.proxies.update({
            "http": proxy_pool.get_one(),
        })

# 页面缓存，防止重复采集，提高效率
page_cache: Dict[int, str] = {}


class Fragment(object):
    def __init__(self, title: str, d: date, link: str, cover_url: Optional[str] = None):
        self.title = title
        self.date = d
        self.link = link
        self.cover_url = cover_url
        self.video_url: Optional[str] = None

    def __repr__(self):
        return f'<Fragment {self.title}>'

    def to_json(self):
        return {
            'title': self.title,
            'date': self.date.strftime('%Y-%m-%d'),
            'link': self.link,
            'cover_url': self.cover_url,
            'video_url': self.video_url
        }


def extract_date(title: str) -> Optional[date]:
    result = DATE_PATTERN.search(title)

    if not result:
        logger.warning(f'无法从标题 [{title}] 提取日期')
        return None

    d = date.fromisoformat(result.group(0))
    logger.debug(f'成功从标题 [{title}] 中提取日期 [{d}]')
    return d


def download_video(video_url: str, save_dir: str):
    logger.debug(f'正在下载视频 {video_url}')
    result = session.get(video_url)
    with open(os.path.join(save_dir, f'{uuid.uuid4().hex}.mp4'), 'wb') as f:
        f.write(result.content)


def get_video_url(f: Fragment) -> Optional[str]:
    logger.debug(f'分析：{f.link}')
    html = session.get(f.link)
    soup = BeautifulSoup(html.content, 'html.parser')
    video_elem = soup.select_one(
        'body > div > div > div > div.text-center.content > video')
    if not video_elem:
        logger.error(f'无法获取 [{f.title}] 的视频元素！')
        return None

    return video_elem.attrs.get('src', None)


def crawl_page(page_number: int = 1):
    if page_number in page_cache:
        logger.debug(f'采集页面 [{page_number}] 命中缓存')
        return page_cache[page_number]

    if page_number <= 1:
        url = 'https://strtv.dahuawang.com/b/a/list_dahua.shtml'
    else:
        url = f'https://strtv.dahuawang.com/b/a/list_more_dahua_{page_number}.html'

    logger.debug(f'正在请求地址: {url}')

    html = session.get(url).content.decode('utf-8')
    page_cache[page_number] = html

    logger.debug(f'采集页面 [{page_number}] 完成，等待 1000 毫秒')
    time.sleep(1)

    return html


def get_fragments(assign_date: date) -> List[Fragment]:
    today = datetime.datetime.now().date()
    delta_days = (today - assign_date).days

    page_range_s = 1
    page_range_e = 3

    if delta_days > 2:
        page_range_s = delta_days - 3
        page_range_e = page_range_s + 3

    logger.info(f'指定日期与今天相差 {delta_days}，决定采集页面范围 [{page_range_s}, {page_range_e}]')

    prefix = 'https://strtv.dahuawang.com'

    fragments_dict = {}

    for i in range(page_range_s, page_range_e + 1):
        logger.info(f'正在获取第 {i} 页')

        html = crawl_page(i)
        soup = BeautifulSoup(html, 'html.parser')
        elems = soup.select('li.news-item')
        for elem in elems:
            title = elem.select_one('.text-box .tit a').text
            d = extract_date(title)
            if d != assign_date:
                logger.debug(f'不是指定日期，跳过 [{title}]')
                continue
            title = title.replace(f'{d}', '').strip()
            link = elem.select_one('.text-box a').attrs.get('href', None)
            cover_url = elem.select_one('.img-box img').attrs.get('src', None)

            if link:
                link = prefix + link
            else:
                logger.error(f'无法获取 [{title}] 的地址')
                continue

            f = Fragment(title=title, d=d, link=link, cover_url=cover_url)

            if f.title in fragments_dict:
                logger.debug(f'片段 {f.title} 已存在，跳过')
                continue

            f.video_url = get_video_url(f)
            fragments_dict[f.title] = f

            logger.debug(f'等待 1000 毫秒')
            time.sleep(1)

    fragments = [f for f in fragments_dict.values()]

    with open(os.path.join(CONFIG['base_dir'], 'downloads', f'{assign_date}.json'), 'w', encoding='utf-8') as f:
        logger.debug(f'日期 {assign_date} 片段信息写入文件')
        json.dump([e.to_json() for e in fragments], f, indent=2, ensure_ascii=False)

    return fragments


def check_date_has_updated(assign_date: date):
    """检查指定日期是否已更新"""
    html = crawl_page(1)
    soup = BeautifulSoup(html, 'html.parser')
    elems = soup.select('body > div.content-box.clearfix > div > ul > li')
    for elem in elems:
        title = elem.select_one('.text-box .tit a').text
        d = extract_date(title)
        logger.debug(f'检查 - {title}')

        if d == assign_date:
            return True

    return False


def videos_merge(videos_dir: str, output_path: str):
    import os
    import tempfile
    from ffmpy import FFmpeg
    videos = []
    for item in os.listdir(videos_dir):
        if item.endswith('.mp4'):
            videos.append(os.path.abspath(os.path.join(
                videos_dir, item)).replace('\\', '/'))

    if len(videos) == 0:
        logger.warning('没有需要合并的视频，退出')
        return

    concat_file = tempfile.mktemp(prefix='st-tv_', suffix='.txt')
    logger.info(f'创建临时文件作为视频合并列表：{concat_file}')
    with open(concat_file, 'w+', encoding='utf-8') as f:
        f.write('\n'.join(f'file {item}' for item in videos))

    logger.info(f'正在合并 {len(videos)} 个视频')
    ff = FFmpeg(
        global_options=['-f', 'concat',
                        '-safe', '0'],
        inputs={concat_file: None},
        outputs={output_path.replace('\\', '/'): ['-c', 'copy']}
    )
    logger.debug(f'ffmpeg cmd: {ff.cmd}')
    ff.run()
    logger.debug('合并完成')

    logger.info(f'清理临时文件：{concat_file}')
    os.remove(concat_file)


def crawl_tv(d: date):
    logger.info(f'采集日期 [{d}] 的今日视线')
    fragments = get_fragments(d)

    cache_dir = os.path.join(CONFIG['base_dir'], 'downloads', f'{d}')
    output_dir = CONFIG['output_dir']
    os.makedirs(cache_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    for item in fragments:
        if not item.video_url:
            continue
        download_video(item.video_url, cache_dir)

        logger.debug(f'等待 1000 毫秒')
        time.sleep(1)

    logger.info('开始合并视频')
    videos_merge(cache_dir, os.path.join(output_dir, f'{d}.mp4'))
    logger.info(f'清理已下载的视频，删除：{cache_dir}')
    shutil.rmtree(cache_dir)


def run():
    logger.info('启动！')
    date_list: List[date] = [
        # datetime.datetime.now().date(),
        (datetime.datetime.now() - timedelta(days=1)).date(),
        # datetime.datetime.strptime('2024-07-09', '%Y-%m-%d').date(),
        # datetime.datetime.strptime('2024-07-10', '%Y-%m-%d').date(),
        # datetime.datetime.strptime('2024-07-11', '%Y-%m-%d').date(),
        # datetime.datetime.strptime('2024-07-12', '%Y-%m-%d').date(),
        # datetime.datetime.strptime('2024-07-13', '%Y-%m-%d').date(),
    ]
    for d in date_list:
        logger.info(f'正在执行 [{d}] 的任务')
        crawl_tv(d)
        logger.info(f'{d} 任务完成，等待5秒')
        time.sleep(5)


if __name__ == '__main__':
    run()
    # whats_my_ip()
    # test_sttv()
    # print('今天的视线更新了吗？', check_date_has_updated(datetime.datetime.now().date()))
    ...
