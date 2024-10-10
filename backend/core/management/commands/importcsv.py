from csv import DictReader

from django.core.management import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


DATA_FILES = {
    'ingredients': (
        'ingredients.csv',
        Ingredient,
        ['id', 'name', 'measurement_unit']
    ),
}

DATA_DIR = settings.BASE_DIR / 'data'
FILE_NAME = 'ingredients.csv'
csv_file = DATA_DIR / FILE_NAME


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(csv_file, type=str)

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        try:
            with open(csv_file, newline='') as f:
                reader = DictReader(f)
                for row in reader:
                    row.pop('id', None)
                    Ingredient.objects.create(**row)

            self.stdout.write(self.style.SUCCESS('Данные загружены.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Файл не найден.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
