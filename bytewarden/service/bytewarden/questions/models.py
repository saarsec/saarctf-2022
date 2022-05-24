from django.db import models
from users.models import CustomUser

DEFAULT_QUESTIONS = [
	"Question01",
	"Question02",
	"Question03",
	"Question04",
	"Question05",
	"Question06",
	"Question07",
	"Question08",
	"Question09",
	"Question10",
]

class Question(models.Model):
	user	 	  = models.ForeignKey(CustomUser, on_delete = models.CASCADE)
	question_num  = models.IntegerField()
	question_text = models.CharField(max_length = 50)
	answer_text   = models.CharField(max_length = 100)
	is_shared 	  = models.BooleanField(default = False) 

	def __str__(self):
		shared = "Shared" if self.is_shared else "Not Shared"
		return f"{self.user.username}: {repr(self.question_text)} {repr(self.answer_text)} {shared}" 
