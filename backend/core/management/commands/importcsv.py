from csv import DictReader
from django.core.management import BaseCommand
from django.conf import settings

from recepies.models import Ingredient
from users.models import User


DATA_FILES = {
    'ingredients': ('ingredients.csv', Ingredient, ['name', 'measurement_unit']),
}

DATA_DIR = settings.BASE_DIR /'data'


class Command(BaseCommand):

    FILE_NOT_FOUND = 'Файл {file_path} не найден.'
    MODEL_ADDED = "{model_name} добавлены: {loaded_info}"
    NO_NEW_RECORDS = "Новые {model_name} не были добавлены."
    MODEL_SKIPPED = "{model_name} пропущены: {skipped_info}"

    def handle(self, *args, **options):
        """Импорт данных из CSV файлов."""
        for key, (file_name, model, fields) in DATA_FILES.items():
            foreign_keys = self.get_foreign_keys(key)
            self.load_data(file_name, model, fields, foreign_keys)

    def get_foreign_keys(self, key):
        """Возвращает словарь с внешними ключами."""
        return {
            'titles': {'category': Category},
            'review': {'title_id': Title, 'author': User},
            'comments': {'review_id': Review, 'author': User},
            'genre_title': {'title_id': Title, 'genre_id': Genre}
        }.get(key, {})

    def load_data(self, file_name, model, fields, foreign_keys=None):
        """Загружает данные из CSV файла в модель."""
        file_path = DATA_DIR / file_name

        if not self.file_exists(file_path):
            return

        existing_ids = self.get_existing_ids(model)
        loaded, skipped = self.process_csv(
            file_path, model, fields, foreign_keys, existing_ids)

        self.report_results(model, loaded, skipped)

    def file_exists(self, file_path):
        """Проверяет, существует ли файл."""
        if not file_path.exists():
            self.stdout.write(self.style.ERROR(
                self.FILE_NOT_FOUND.format(file_path=file_path)))
            return False
        return True

    def read_csv(self, file_path):
        """Генератор для чтения строк из CSV файла."""
        with file_path.open('r', encoding='utf-8') as csvfile:
            reader = DictReader(csvfile)
            for row in reader:
                yield row

    def get_existing_ids(self, model):
        """Получает идентификаторы существующих объектов модели из БД."""
        return set(map(str, model.objects.values_list('id', flat=True)))

    def process_csv(
            self, file_path, model, fields, foreign_keys, existing_ids):
        """Обрабатывает CSV файл и возвращает списки записей."""
        loaded = []
        skipped = []

        for row in self.read_csv(file_path):
            if row['id'] in existing_ids:
                skipped.append(row['id'])
                continue

            model_data = self.prepare_model_data(row, fields, foreign_keys)
            self.save_model_instance(model, model_data, loaded)

        return loaded, skipped

    def prepare_model_data(self, row, fields, foreign_keys):
        """Подготавливает данные для создания объекта модели."""
        model_data = {field: row[field] for field in fields}

        for field, related_model in foreign_keys.items():
            related_instance = related_model.objects.get(id=row[field])
            model_data[field.replace('_id', '')] = related_instance

        return model_data

    def save_model_instance(self, model, model_data, loaded):
        """Создает и сохраняет экземпляр модели в базе данных."""
        if model == Title.genre.through:
            title = model_data['title']
            genre = model_data['genre']
            title.genre.add(genre)
        else:
            model_instance = model(**model_data)
            model_instance.save()
        loaded.append(model_data['id'])

    def report_results(self, model, loaded, skipped):
        """Выводит отчет о загруженных и пропущенных записях."""

        if model == Title.genre.through:
            model_name = "TitleGenre"
        else:
            model_name = model.__name__

        if loaded:
            loaded_info = ', '.join(loaded)
            self.stdout.write(self.style.SUCCESS(
                self.MODEL_ADDED.format(
                    model_name=model_name, loaded_info=loaded_info)
            ))
        else:
            self.stdout.write(self.style.WARNING(
                self.NO_NEW_RECORDS.format(model_name=model_name)
            ))

        if skipped:
            skipped_info = ', '.join(skipped)
            self.stdout.write(self.style.WARNING(
                self.MODEL_SKIPPED.format(
                    model_name=model_name, skipped_info=skipped_info)
            ))
