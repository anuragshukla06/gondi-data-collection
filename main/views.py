from django.shortcuts import render
from django.http import HttpResponse
from . import models
import pandas as pd
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

data = pd.read_csv("https://github.com/cgnetswara/TransDataCollectionBackend/raw/master/projectBackEnd/main/res/hindi_sentences.csv", delimiter = '\t', names=["tatoeba", "number", "hindi"])

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

@csrf_exempt
def submitAnswer(request):
    if request.method == 'POST':
        dicti = {}
        params = request.POST
        phone = params['phone']; answer = params['answer']; addPoint = int(params['addPoint']); regionId = params['regionId']
        userObject = models.user.objects.get(phone=phone)
        translationObject = models.translation(questionId=userObject.progress, question=data['hindi'].iloc[userObject.progress], answer=answer,regionId=regionId, by=userObject)
        translationObject.save()
        userObject.progress += 1
        userObject.points += addPoint
        userObject.save()

        dicti['phone'] = userObject.phone
        dicti['progress'] = userObject.progress
        dicti['points'] = userObject.points
        return HttpResponse(json.dumps((dicti)))

@csrf_exempt
def fetchQuestion(request):
    if request.method == 'POST':
        # possible optimisation if progress is saved locally.
        # Take care of database end case
        userObject = models.user.objects.get(phone=request.POST['phone'])
        progress = userObject.progress
        # print(data.head())
        if progress >= len(data['hindi']):
            return HttpResponse("EOF")
        return HttpResponse(data['hindi'].iloc[progress])