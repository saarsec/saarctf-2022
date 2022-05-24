from django.contrib.auth.models import User
from django.db import models


class Loop(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    public = models.BooleanField(default=False)
    bpm = models.IntegerField()
    length = models.IntegerField()


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    loop = models.ForeignKey(Loop, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'loop'], name='unique_votes')
        ]
