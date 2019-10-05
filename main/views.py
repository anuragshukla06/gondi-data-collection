from django.shortcuts import render
from django.http import HttpResponse
from . import models
import pandas as pd
import json
# Create your views here.

data = pd.read_excel('https://srv-file7.gofile.io/download/VYSJAm/wordsData.xlsx')

def index(request):
    return HttpResponse("This was successfull")

def verifyOrRegister(request, phone):
    dicti = {}
    userObject = None
    if not(models.user.objects.filter(phone = phone).exists()):
        userObject = models.user(phone=phone, progress=0, points=0)
        userObject.save()
    else:
        userObject = models.user.objects.get(phone=phone)
    dicti['progress'] = userObject.progress #progress is the amount of questions translated by a user and also reflects current id of question asked (not answered).
    dicti['phone'] = userObject.phone
    dicti['points'] = userObject.points


    return HttpResponse(json.dumps(dicti)) #Add code to actually check successful submission

def submitAnswer(request, phone, answer, addPoint):
    dicti = {}
    userObject = models.user.objects.get(phone=phone)
    translationObject = models.translation(questionId=userObject.progress, question=data.iloc[userObject.progress]['Hindi'], answer=answer, by=userObject)
    translationObject.save()
    userObject.progress += 1
    userObject.points += addPoint
    userObject.save()

    dicti['phone'] = userObject.phone
    dicti['progress'] = userObject.progress
    dicti['points'] = userObject.points
    return HttpResponse(json.dumps((dicti)))

def fetchQuestion(request, phone):
    # possible optimisation if progress is saved locally.
    # Take care of database end case
    userObject = models.user.objects.get(phone=phone)
    progress = userObject.progress
    return HttpResponse(data.iloc[progress]['Hindi'])