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
import schedule
from django.template import loader
from django.db.models import Count
# Create your views here.
# print("YES")


            



class EmailThread (threading.Thread):
    def send_report():
        print("Starting_mail_report")
        admin_mails = [
            'shukla.anurag0006@gmail.com',
            'kalikabali@gmail.com',
            'smitashu@gmail.com',
            'devansh76@gmail.com,'
            'diptendudip@gmail.com',
            'vishnuprasad.k214@gmail.com',
            'sebastinssanty@gmail.com',
        ]
        from_mail = 'aadivasiswara@gmail.com'
        last_time = datetime.datetime.now()-datetime.timedelta(1)
        last_regs = models.user.objects.filter(register_time__gte = last_time).count()
        last_trans = models.translation.objects.filter(time__gte = last_time).count()
        total_regs = models.user.objects.all().count()
        total_trans = models.translation.objects.all().count()


        html_text = loader.render_to_string('Email/report_email.html', {'details': {"last_regs": last_regs,
                                                                                    "last_trans": last_trans,
                                                                                    "total_trans": total_trans,
                                                                                    "total_regs": total_regs,
                                                                                    "from": last_time,
                                                                                    "to": datetime.datetime.now()} })
        print(last_regs, last_trans, total_regs, total_trans)

        subject = "Adivasi Swara Activity Report"
        send_mail(subject, 'plain_text', from_mail, admin_mails, html_message=html_text)
        print("email sent")

    def run(self):
        EmailThread.send_report()
        schedule.every().day.at("00:00").do(EmailThread.send_report)
        while True: 
    
            # Checks whether a scheduled task  
            # is pending to run or not 
            schedule.run_pending() 
            time.sleep(300) 
            total_regs = models.user.objects.all().count() # hack to get around database timeout issue
    

data = pd.read_csv("https://github.com/cgnetswara/TransDataCollectionBackend/raw/master/projectBackEnd/main/res/hindi_sentences.csv", delimiter = '\t', names=["tatoeba", "number", "hindi"])

emailThread = EmailThread()
emailThread.start()

def index(request):
    return HttpResponse("This was successfull")

def verifyOrRegister(request, phone):
    dicti = {}
    userObject = None
    if not(models.user.objects.filter(phone = phone).exists()):
        userObject = models.user(phone=phone, progress=0, points=0, register_time=datetime.datetime.now())
        userObject.save()
    else:
        userObject = models.user.objects.get(phone=phone)
    dicti['progress'] = userObject.trans_num #progress (in the dictionary) is the amount of questions translated by a user
    dicti['phone'] = userObject.phone
    dicti['points'] = userObject.points


    return HttpResponse(json.dumps(dicti)) #Add code to actually check successful submission

def update_progress(userObject):
    userObject.progress += 1
    total_translated = models.total_translated.objects.latest('id')
    total_translated.progress += 1
    total_translated.save()

def trans_num_details(request):
    return render(request, 'main/trans_num.html', {'user_data': models.user.objects.all().order_by('-trans_num')})

@csrf_exempt
def submitAnswer(request):
    if request.method == 'POST':
        dicti = {}
        params = request.POST
        phone = params['phone']; answer = params['answer']; addPoint = int(params['addPoint']); regionId = params['regionId']
        userObject = models.user.objects.get(phone=phone)
        print(answer, 'answer_debug')
        # f = open("test.txt", "w")
        # f.write(answer)
        # f.close()
        translationObject = models.translation(questionId=userObject.progress, 
                                                    question=data['hindi'].iloc[userObject.progress], 
                                                    answer=answer,regionId=regionId, 
                                                    by=userObject,
                                                    time=datetime.datetime.now())
        print(translationObject.answer, 'answer_debug_after_database')
        translationObject.save()
        update_progress(userObject)
        userObject.points += addPoint
        userObject.trans_num += 1
        userObject.save()

        dicti['phone'] = userObject.phone
        dicti['progress'] = userObject.trans_num
        dicti['points'] = userObject.points
        return HttpResponse(json.dumps((dicti)))

@csrf_exempt
def fetchQuestion(request):
    if request.method == 'POST':
        # possible optimisation if progress is saved locally.
        # Take care of database end case
        userObject = models.user.objects.get(phone=request.POST['phone'])
        total_translated = models.total_translated.objects.latest('id').progress
        userObject.progress = total_translated
        userObject.save()
        # print(data.head())
        if total_translated >= len(data['hindi']):
            return HttpResponse("EOF")
        return HttpResponse(data['hindi'].iloc[total_translated])