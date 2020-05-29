from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from . import models
import pandas as pd
import json
import xlsxwriter
import os
from django.core.mail import send_mail, EmailMessage
from django.views.decorators.csrf import csrf_exempt
import datetime, time
import threading
from django.core.mail import send_mail
import schedule
from django.template import loader
from django.db.models import Count
from .serializers import FileSerializer
from django.core.files.base import ContentFile
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
            'cgnetswara002@gmail.com',
            'shu@cgnet.in'
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
        print("Stats email sent")

        ########## SENDING LEADER WISE REPORT ###############

                # - FIRST TIME DATA FILL UP INITIALIZATION CODE (DO NOT RUN AT THE RUNTIME, KEEP IT COMMENTED)
        

        # team_data = pd.read_excel("C:\\Users\\lenovo\\Projects\\gondi-data-collection\\main\\res\\team_data.xlsx")
        # team_data.dropna(how='all')
        # print(team_data)
        # last_leader = None

        # for i in range(len(team_data)):
        #     if not(pd.isnull(team_data['Leaders Name'].iloc[i])):
        #         last_leader = team_data['Contact Number '].iloc[i]
        #         last_leader = models.user.objects.filter(phone = last_leader)
        #         if len(last_leader):
        #             last_leader = last_leader[0]
        #             last_leader.leader = LEADER
        #             last_leader.save()
            
        #     else:
        #         if last_leader:
        #             member_ph = team_data['Contact Number '].iloc[i]
        #             member = models.user.objects.filter(phone = member_ph)
        #             if member:
        #                 member = member[0]
        #                 member.leader = last_leader
        #                 member.save()


        #### MAKING REPORT #######
        LEADER = models.user.objects.get(phone='LEADER')
        leaders = models.user.objects.filter(leader = LEADER)
        str_date = datetime.datetime.now().strftime("%m_%d_%Y")
        DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res\leader_report")
        filename = os.path.join(DIR, "Leaderwise_Report_" + str_date + ".xlsx")
        print(filename, "hjdbjhdcsdbchsbcjkdsb")

        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet()

        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'yellow'}) #Fancy heading for leader
        
        column_head_format = workbook.add_format( {
            'bold': 1
        })
        row = 0
        col = 0
        for leader in leaders:
            # Add heading here with leader phone number
            total = leader.trans_num # Total translations by a group
            worksheet.merge_range(row, col, row, col+1, "LEADER: " + leader.phone, merge_format)
            
            row += 1
            worksheet.write(row, col, 'PHONE', column_head_format)
            worksheet.write(row, col+1, 'Number of Translations', column_head_format)
            row += 1
            #Add Another heading for column heads

            worksheet.write(row, col, leader.phone)
            worksheet.write(row, col, leader.trans_num)

            members = models.user.objects.filter(leader=leader)
            for member in members:
                worksheet.write(row, col, member.phone)
                worksheet.write(row, col+1, member.trans_num)
                total += member.trans_num
                row += 1
            
            # Add a Total Field (in BOLD, include leader's count)
            worksheet.write(row, col, "Total")
            worksheet.write(row, col+1, total)
            row += 1

        workbook.close()


        #### SENDING REPORT VIA EMAIL #####

        leader_rep_mail = EmailMessage(
        'Leader Wise Report',
        'Find attached leaderwise report',
        from_mail,
        ['shukla.anurag0006@gmail.com', 'shu@cgnet.in', 'cgnetswara002@gmail.com'],
        )

        leader_rep_mail.attach_file(filename)
        leader_rep_mail.send()

        print("Leader wise report sent.")

        

    def run(self):
        EmailThread.send_report()
        schedule.every().day.at("00:00").do(EmailThread.send_report)
        while True: 
    
            # Checks whether a scheduled task  
            # is pending to run or not 
            schedule.run_pending() 
            time.sleep(120) 
            total_regs = models.user.objects.all().count() # hack to get around database timeout issue
    

data = pd.read_csv("https://github.com/cgnetswara/TransDataCollectionBackend/raw/master/projectBackEnd/main/res/hindi_sentences.csv", delimiter = '\t', names=["tatoeba", "number", "hindi"])

emailThread = EmailThread()
emailThread.start() 
##TODO: Uncomment this

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
        phone = params['phone']; answer = params['answer']; addPoint = int(params['addPoint']); regionId = params['regionId'];
        userObject = models.user.objects.get(phone=phone)
        print(answer, 'answer_debug')
        # f = open("test.txt", "w")
        # f.write(answer)
        # f.close()

        files = request.FILES.getlist('files')
        up_file = None
        if len(files):
            up_file = files[0]
            up_file.name = str(userObject.progress) + ".mp3"
        translationObject = models.translation(questionId=userObject.progress, 
                                                    question=data['hindi'].iloc[userObject.progress], 
                                                    answer=answer,regionId=regionId, 
                                                    by=userObject,
                                                    time=datetime.datetime.now(),
                                                    speech=up_file)
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

def fetchQuestionOffline(request, num):

    total_translated = models.total_translated.objects.latest('id')
    arr = []
    for i in range(total_translated.progress, total_translated.progress+num):
        arr.append({'qId': i, 'question':data['hindi'].iloc[i]})
    total_translated.progress += num 
    total_translated.save()
    response = {'response': arr}
    print(response)
    return HttpResponse(json.dumps(response, ensure_ascii=False))

'''
The Post request has arguments:
    answers: JSON Array of responses [ {"qId": integer, "translation": string, "regionId": Integer} ]
    phone: Phone number of the user
'''
@csrf_exempt
def submitAnswerOffline(request):
    if request.method == 'POST':
        # possible optimisation if progress is saved locally. 
        # Take care of database end case
        print()
        params = request.POST
        json_arr = params['answers']; phone = params['phone'];
        files = request.FILES.getlist('files');


        # print(json_arr, type(json_arr))
        userObject = models.user.objects.get(phone=phone)
        responses = json.loads(json_arr)

        for responseI in range(len(responses)):
            up_file = None
            if len(files):
                up_file = files[responseI]
                up_file.name = str(responses[responseI]['qId']) + ".mp3"
            translationObject = models.translation(questionId=responses[responseI]['qId'], 
                                                    question=data['hindi'].iloc[responses[responseI]['qId']], 
                                                    answer=responses[responseI]['translation'],regionId=responses[responseI]['regionId'], 
                                                    by=userObject,
                                                    time=datetime.datetime.now(),
                                                    speech=up_file)
            
            userObject.trans_num += 1
            userObject.points += 1
            translationObject.save()
        userObject.save()
        return HttpResponse("SUCCESS")

@csrf_exempt
def aud_upload(request):

    # up_file = request.FILES['file']
    # up_file.name = "random.mp3"
    files = request.FILES.getlist('files')
    print(len(files))
    for i in files:
        temp = models.tempModel(name='anurag', file=i)
        temp.save()
    return HttpResponse("SUCCESS")

    # file_serializer = FileSerializer(data=request.FILES)
    # if file_serializer.is_valid():
    #     data = file_serializer['file']
    #     print(type(data))
    #     obj = models.tempModel(name=request.POST['name'], file=data)
    #     obj.save()