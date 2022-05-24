from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    code = models.CharField(max_length = 10, blank = True)
    used_recovery_login = models.BooleanField(default = False)
