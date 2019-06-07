from django.db import models

# Create your models here.


class TweetDumps(models.Model):
    PENDING = 'PEN'
    PROCESSED = 'PRO'
    STAUS_CHOICES = (
        (PENDING, 'Pending'),
        (PROCESSED, 'Processed')
    )

    path = models.CharField(max_length=2, unique=True)
    status = models.CharField(
        max_length=50,
        choices=STAUS_CHOICES,
        default=PENDING
    )
    time = models.DateTimeField()

    def __str__(self):
        return self.path


class TweetCountSummary(models.Model):
    party = models.CharField(max_length=30)
    count = models.IntegerField()
    time = models.DateTimeField()
