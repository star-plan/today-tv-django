"""面向访客的节目页面测试，而非早期未公开的后台 CRUD 测试。"""

from datetime import datetime

from django.test import TestCase
from django.urls import reverse

from apps.television.models import TvProgram, Video


class VideoPageTests(TestCase):
    """确认真实用户访问归档和播放器时能看到可播放内容。"""

    def setUp(self):
        self.program = TvProgram.objects.create(
            name='今日视线',
            source_url='https://strtv.dahuawang.com/b/a/list_dahua.shtml',
            status=TvProgram.Status.UPDATED,
        )
        self.first_video = Video.objects.create(
            program=self.program,
            name='关注城市里的民生小事',
            time=datetime(2026, 8, 8),
            related_link='https://example.test/detail/1',
            video_link='https://media.example.test/1.mp4',
            source_key='1' * 64,
        )
        self.second_video = Video.objects.create(
            program=self.program,
            name='同日第二个节目片段',
            time=datetime(2026, 8, 8),
            related_link='https://example.test/detail/2',
            video_link='https://media.example.test/2.mp4',
            source_key='2' * 64,
        )

    def test_archive_can_be_opened_without_login(self):
        """节目归档是公开内容，不能再被登录装饰器拦住。"""
        response = self.client.get(reverse('television:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_video.name)

    def test_player_contains_source_url_and_next_episode(self):
        """播放器输出源站地址，并把同日下一条节目交给前端自动连播。"""
        response = self.client.get(reverse('television:video', kwargs={'pk': self.first_video.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.first_video.video_link)
        self.assertContains(response, reverse('television:video', kwargs={'pk': self.second_video.id}))
