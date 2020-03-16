from django.shortcuts import render
from django.http import HttpResponse
from . import models
import pandas as pd
import json
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
import datetime, time
import threading
from django.core.mail import send_mail
from django.template import loader
# Create your views here.
# print("YES")



class EmailThread (threading.Thread):
    def run(self):
        admin_mails = [
            'shukla.anurag0006@gmail.com',
        ]
        from_mail = 'shukla.anurag0006@gmail.com'
        print ("Starting " + self.name)
        while True:
            last_time = datetime.datetime.now()
            day_registrations = models.user.objects.filter(register_time__gte = last_time).count()
            day_translations = models.translation.objects.filter(time__gte = last_time).count()
            html_text = loader.render_to_string('Email/report_email.html', {'details': {"regs": day_registrations,
                                                                                        "trans": day_translations,
                                                                                        "from": last_time,
                                                                                        "to": datetime.datetime.now()} })
            subject = "Adivasi Swara Activity Report"
            send_mail(subject, 'plain_text', from_mail, admin_mails, html_message=html_text)
            print("email sent")
            time.sleep(24*60*60) #delay in seconds
        print ("Exiting " + self.name)

data = pd.read_csv("https://github.com/cgnetswara/TransDataCollectionBackend/raw/master/projectBackEnd/main/res/hindi_sentences.csv", delimiter = '\t', names=["tatoeba", "number", "hindi"])

emailThread = EmailThread()
emailThread.start()

def index(request):
    return HttpResponse("This was successfull")

def verifyOrRegister(request, phone):
    dicti = {}
    userObject = None
    if not(models.user.objects.filter(phone = phone).exists()):
        userObject = models.user(phone=phone, progress=0, points=0, time=datetime.datetime.now())
        userObject.save()
    else:
        userObject = models.user.objects.get(phone=phone)
    dicti['progress'] = userObject.progress #progress is the amount of questions translated by a user and also reflects current id of question asked (not answered).
    dicti['phone'] = userObject.phone
    dicti['points'] = userObject.points


    return HttpResponse(json.dumps(dicti)) #Add code to actually check successful submission

def update_progress(userObject):
    userObject.progress += 1
    total_translated = models.total_translated.objects.latest('id')
    total_translated.progress += 1
    total_translated.save()

@csrf_exempt
def submitAnswer(request):
    if request.method == 'POST':
        dicti = {}
        params = request.POST
        phone = params['phone']; answer = params['answer']; addPoint = int(params['addPoint']); regionId = params['regionId']
        userObject = models.user.objects.get(phone=phone)
        
        translationObject = models.translation(questionId=userObject.progress, 
                                                    question=data['hindi'].iloc[userObject.progress], 
                                                    answer=answer,regionId=regionId, 
                                                    by=userObject,
                                                    time=datetime.datetime.now())
        translationObject.save()
        update_progress(userObject)
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
        total_translated = models.total_translated.objects.latest('id').progress
        # print(data.head())
        if total_translated >= len(data['hindi']):
            return HttpResponse("EOF")
        return HttpResponse(data['hindi'].iloc[total_translated])