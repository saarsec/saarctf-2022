from django.db import models
from users.models import CustomUser

class Password(models.Model):
	password_num = models.IntegerField()
	user	 = models.ForeignKey(CustomUser, on_delete = models.CASCADE, related_name = '+')
	title 	 = models.CharField(max_length = 20)
	url 	 = models.CharField(max_length = 50)
	password = models.CharField(max_length = 50)

	def __str__(self):
		return f"{self.user.username}: {repr(self.title)}, {repr(self.url)}, {repr(self.password)}" 
