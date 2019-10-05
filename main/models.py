from django.db import models

# Create your models here.
class user(models.Model):
    phone = models.CharField(max_length=10)
    progress = models.IntegerField()
    points = models.IntegerField()

    def __str__(self):
        return str(self.phone) + " | " + str(self.progress)

class translation(models.Model):
    questionId = models.IntegerField()
    regionId = models.IntegerField()
    question = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)
    by = models.ForeignKey(user, on_delete=models.CASCADE)

    def __str__(self):
        return "Id:" + str(self.questionId) +" | " + str(self.question)[:5] + " | " + str(self.answer)[:5] + " | " + str(self.by.phone)
