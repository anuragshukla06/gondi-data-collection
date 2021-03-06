from django.db import models
import datetime

# Create your models here.
class user(models.Model):
    phone = models.CharField(max_length=10)
    points = models.IntegerField()
    progress = models.IntegerField(editable=False)
    register_time = models.DateTimeField(default=datetime.datetime.now())
    trans_num = models.IntegerField(editable=False, default=0) # Number of translations by a user
    leader = models.ForeignKey('self',default = None, on_delete=models.SET_NULL, null=True, editable=True) 
    ordering = ('-trans_num',)

    def __str__(self):
        return str(self.phone) + " | " + str(self.trans_num)

class translation(models.Model):
    questionId = models.IntegerField()
    regionId = models.IntegerField()
    question = models.CharField(max_length=1000)
    answer = models.CharField(max_length=1000)
    by = models.ForeignKey(user, on_delete=models.CASCADE)
    time = models.DateTimeField(default=datetime.datetime.now())
    speech = models.FileField(default=None)

    def __str__(self):
        return "Id:" + str(self.questionId) +" | " + str(self.question)[:5] + " | " + str(self.answer)[:5] + " | " + str(self.by.phone)

class total_translated(models.Model):
    progress = models.IntegerField()

class tempModel(models.Model):
    name = models.CharField(max_length=10)
    file = models.FileField()