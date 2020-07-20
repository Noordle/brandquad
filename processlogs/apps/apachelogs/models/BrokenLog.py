from django.db import models


class BrokenLog(models.Model):
    text = models.TextField(
	    verbose_name='Text from broken log',
	    max_length=10000
    )
