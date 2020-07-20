from django.db import models

from processlogs.apps.apachelogs.constants import HTTPMethods


class ApacheLog(models.Model):
    ipv4_address = models.GenericIPAddressField(
        verbose_name='IPv4 address',
        help_text='IP адрес хоста в лог файле',
    )
    date_logged = models.DateTimeField(
        verbose_name='Datetime of log',
    )
    url = models.CharField(
        verbose_name='URL of response',
        max_length=10000,
    )
    http_method = models.CharField(
        verbose_name='HTTP method',
        max_length=10,
        choices=HTTPMethods.choices(),
        default=HTTPMethods.UNKNOWN,
    )
    status_code = models.PositiveSmallIntegerField(
        verbose_name='HTTP response status code',
    )
    content_length = models.PositiveIntegerField(
        verbose_name='Content-Length',
    )

    def __str__(self):
        return f'{self.ipv4_address} - - [{self.date_logged}] ' \
               f'"{self.http_method} {self.url}" {self.status_code} {self.content_length}'
