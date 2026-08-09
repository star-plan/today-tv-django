"""使用固定 HTML 夹具验证采集解析，不依赖不稳定的外部网络。"""

from datetime import date

from django.test import SimpleTestCase

from apps.television.crawls.swatow_tv import TodayTVCrawler


class TodayTVCrawlerParserTests(SimpleTestCase):
    """源站页面小幅变化时，至少保证列表和播放器地址的核心解析逻辑可回归。"""

    def setUp(self):
        self.crawler = TodayTVCrawler()

    def test_listing_and_detail_are_joined_to_absolute_urls(self):
        """相对链接应转换为 API 和浏览器均可使用的绝对地址。"""
        listing_html = '''
            <ul><li class="news-item">
              <a href="/detail/cover-only.html"><img src="/covers/cover-only.jpg"></a>
              <div class="img-box"><img data-src="/covers/today.jpg"></div>
              <div class="text-box"><h3 class="tit"><a href="/detail/episode-1.html">今日视线 2026-08-08</a></h3></div>
            </li></ul>
        '''
        fragments = self.crawler.parse_listing(listing_html, 'https://source.example/list.html')
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0].published_date, date(2026, 8, 8))
        self.assertEqual(fragments[0].detail_url, 'https://source.example/detail/episode-1.html')

        detailed = self.crawler.parse_detail(fragments[0], '<video><source src="/video/episode-1.mp4"></video>')
        self.assertEqual(detailed.playback_url, 'https://source.example/video/episode-1.mp4')
        self.assertEqual(len(detailed.source_key), 64)
