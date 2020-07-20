import os
import random
import re
import time
from concurrent.futures._base import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
import requests
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator

from processlogs.apps.apachelogs.models import ApacheLog, BrokenLog

DATETIME_FORMAT = '%d/%b/%Y:%H:%M:%S %z'
MAX_LINES_COUNT = 500000
DELETE_AFTER_IMPORT = True


def url_type(value):
    validate = URLValidator()
    try:
        validate(value)
    except ValidationError:
        exit('Введите правильный URL.')
    else:
        return value


class Command(BaseCommand):
    help = 'Команда для парсинга лог-файла веб-сервера Apache'
    requires_migrations_checks = True

    def add_arguments(self, parser):
        parser.add_argument(dest='url', help='Ссылка на лог-файл', action="store", type=url_type)

    def handle(self, *args, **options):
        url = options['url']
        tmp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
        start = time.time()

        # Открываем соединение для скачивания большого файла
        with requests.get(url, stream=True) as r:
            r.raise_for_status()

            # Счетчик i для ограничения скачивания
            i = 0
            for chunk in r.iter_lines(chunk_size=100000, decode_unicode=True):
                if i >= MAX_LINES_COUNT:  # Около 100мб
                    break

                if not chunk:
                    continue

                # Случайное распределение по файлам в зав-ти от кол-ва ядер системы (порядок строк неважен)
                with open(f'{tmp_path}/access_log{random.randint(0, min(32, (os.cpu_count() or 1) + 4) - 1)}', 'at') as f:
                    f.write(f'{chunk}\n')
                i += 1

        download_time = time.time()
        print(f'Скачивание логов: {download_time - start}')

        # Создаем пул потоков, отправляем в каждый функцию для чтения файла, ожидаем строку с завершением обработки
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.bulk_create_logs, f'{tmp_path}/{filename}') for filename in os.listdir(tmp_path)]
            for idx, future in enumerate(as_completed(futures)):
                print(f'Файл №{idx} обработан')

        print(f'Импорт завершен. Время обработки: {time.time() - download_time}')
        if DELETE_AFTER_IMPORT:
            for filename in os.listdir(tmp_path):
                os.unlink(f'{tmp_path}/{filename}')

    def bulk_create_logs(self, filename):
        """
        Функция для чтения лог-файла и массового создания записей в БД
        :param filename: Путь лог-файла
        """
        with open(filename, 'r') as f:
            ApacheLog.objects.bulk_create(filter(lambda x: x is not None,
                                                 [self.parse_line(line) for line in f.readlines() if line]),
                                          batch_size=MAX_LINES_COUNT // 5,
                                          ignore_conflicts=True)

    def parse_line(self, line):
        """
        Функция для парсинга строчки лога
        :param line: строка из лог-файла
        :return: Объект лога если парсинг отработал, если поймано исключение создается строка в таблице для
        битых строк и возвращается None
        """
        try:
            regex_data = re.match(
                r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s\-\s\-\s\[(.+)\]\s\"(\w{1,7})\s(\S*)\s\S*\s(\d*)\s(\d*).*',
                line,
            ).groups()

            return ApacheLog(
                ipv4_address=regex_data[0],
                date_logged=datetime.strptime(regex_data[1], DATETIME_FORMAT),
                http_method=regex_data[2],
                url=regex_data[3],
                status_code=regex_data[4],
                content_length=regex_data[5] or 0,
            )
        except Exception:
            BrokenLog.objects.create(text=line)
