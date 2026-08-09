"""公共客户端 API 的契约测试。"""

from datetime import datetime

from django.test import TestCase

from apps.television.models import TvProgram, Video


class PublicApiTests(TestCase):
    """校验首页客户端所需的节目概览和分页播放数据。"""

    def setUp(self):
        program = TvProgram.objects.create(
            name='今日视线',
            source_url='https://strtv.dahuawang.com/b/a/list_dahua.shtml',
            status=TvProgram.Status.UPDATED,
        )
        Video.objects.create(
            program=program,
            name='客户端可播放的节目',
            time=datetime(2026, 8, 8),
            related_link='https://example.test/detail/api',
            video_link='https://media.example.test/api.mp4',
            source_key='a' * 64,
        )

    def test_program_summary(self):
        """节目概览输出同步状态、库存和最近节目日期。"""
        response = self.client.get('/api/today-tv/program')
        self.assertEqual(response.status_code, 200)
        payload = response.json()['data']
        self.assertEqual(payload['name'], '今日视线')
        self.assertEqual(payload['episode_count'], 1)

    def test_episode_list_is_filterable_and_playable(self):
        """客户端按日期筛选后仍能获得直连播放地址和项目播放页。"""
        response = self.client.get('/api/today-tv/episodes?publish_date=2026-08-08&limit=10')
        self.assertEqual(response.status_code, 200)
        payload = response.json()['data']
        self.assertEqual(payload['count'], 1)
        self.assertEqual(payload['items'][0]['playback_url'], 'https://media.example.test/api.mp4')
        self.assertIn('/tv/video/', payload['items'][0]['webpage_url'])
