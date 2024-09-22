from django.core.management.base import BaseCommand, CommandError
from apps.television.tasks import add


class Command(BaseCommand):
    help = 'TodayTV: A test task'

    def handle(self, *args, **options):
        try:
            task_res = add.delay(2, 2)
            self.stdout.write(f'task_id: {task_res}')

            result = task_res.get(timeout=1)
            self.stdout.write(f'task result: {result}')

        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write(self.style.SUCCESS('task finished'))
