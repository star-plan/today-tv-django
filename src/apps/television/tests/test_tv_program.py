from django.test import TestCase
from django.urls import reverse_lazy
from apps.television.models import TvProgram
from django_starter.contrib.seed import Seeder


# Create your tests here.
class Test(TestCase):
    def setUp(self):
        self.seeder = Seeder()

        instances = []
        for i in range(10):
            instances.append(TvProgram(**self.seeder.seed(TvProgram)))
        TvProgram.objects.bulk_create(instances)

    def test_query(self):
        self.assertGreaterEqual(TvProgram.objects.count(), 10)

    def test_api_create(self):
        data = self.seeder.seed(TvProgram)
        resp = self.client.post(
            reverse_lazy('api:television/tv_program/create'),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

        return resp.json()

    def test_api_retrieve(self):
        item = self.test_api_create()
        resp = self.client.get(reverse_lazy('api:television/tv_program/retrieve', kwargs={'item_id': item['data']['id']}))
        self.assertEqual(resp.status_code, 200)

    def test_api_list(self):
        resp = self.client.get(reverse_lazy('api:television/tv_program/list'))
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.json()['data']['count'], 10)

    def test_api_update(self):
        item = self.test_api_create()
        data = self.seeder.seed(TvProgram)
        resp = self.client.put(
            reverse_lazy('api:television/tv_program/update', kwargs={'item_id': item['data']['id']}),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

    def test_api_partial_update(self):
        item = self.test_api_create()
        data = self.seeder.seed(TvProgram)
        resp = self.client.patch(
            reverse_lazy('api:television/tv_program/partial_update', kwargs={'item_id': item['data']['id']}),
            data=data,
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

    def test_api_destroy(self):
        item = self.test_api_create()
        resp = self.client.delete(
            reverse_lazy('api:television/tv_program/destroy', kwargs={'item_id': item['data']['id']}),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)
        self.assertIsNotNone(resp.json())

        resp = self.client.get(reverse_lazy('api:television/tv_program/retrieve', kwargs={'item_id': item['data']['id']}))
        self.assertEqual(resp.status_code, 404)