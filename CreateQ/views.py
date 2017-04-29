# encoding=utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
# Create your views here.
import os
from sqls import *
from sqls_list import *
from sqls_scholar_list import *
from files import *
from sqls_ans import *


def new_survey(request):
    login_user,uno,pwd,usertype = get_basic_from_session(request)
    able = True
    if login_user == '':
        return HttpResponseRedirect("/users/login/")
    if usertype != 'Scholar':
        able = False
    if request.method == "POST":
        dict = request.POST
        print dict
        # 解析
        survey_title = SurveyTitle()
        survey_title.parse(request.POST)
        survey_detail = SurveyDetail()
        survey_detail.parse(request.POST, login_user, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        survey_questions = SurveyQuestions()
        survey_questions.parse(request.POST)
        add_survey_to_db(survey_title, survey_detail, survey_questions, user='scholar_%d' % uno, pwd=pwd)
        return render(request, 'scholar_list.html', {"username": login_user,"able":able})
    else:
        return render(request, 'create_survey.html', {"username": login_user,"able":able})

def post_survey(request):
    return HttpResponse("fail")

def view_questions(request):
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    if login_user == "":
        return HttpResponseRedirect('/users/login/')
    if request.method == 'GET':
        sno = request.GET.get("sno", -1)
        if sno == -1:
            return HttpResponse("Survey error")
        if "load" in request.GET.keys() and request.GET["load"] == 'true':
            sq = load_questions(sno)
            if sq == None:
                return HttpResponse("Survey not exists")
            return JsonResponse(sq.question_list,safe =False)
        if "check" in request.GET.keys() and request.GET["check"] == 'true':
            json ={}
            json['result'],json['errtext'] = check_legibility(sno,uno)
            json['privacy'] = inform_privacy(sno)
            json['abstract'] = load_brief_summary(sno)
            return JsonResponse(json,safe = False)
        return render(request, 'view_questions.html', {'username': login_user, 'sno': sno})
    if request.method == 'POST':
        dict = request.POST
        print dict
        sa = SurveyAnswer()
        sa.parse(dict,uno,time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        sa.add_to_db()
        return HttpResponse("Success")

def view_files(request):
    return render(request,'view_files.html')

def complete_survey(request):
    login_user = request.session.get("username", "")
    if login_user == '':
        return HttpResponseRedirect("/users/login/")

# for new_task
def upload_data(request,name):
    myFile = request.FILES.get(name, None)  # 获取上传的文件，如果没有文件，则默认为None
    if not myFile:
        print "No file upload!"
    destination = open(os.path.join("/home/aucson/Desktop/receiver",name,myFile.name), 'wb+')  # 打开特定的文件进行二进制的写操作
    for chunk in myFile.chunks():  # 分块写入文件
        destination.write(chunk)
    destination.close()
    print "upload over!"
    return [os.path.join("/home/aucson/Desktop/receiver",name),myFile.name]

def new_task(request):
    #login_user = request.session.get("username", "")
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    able =True
    if login_user == '':
        return HttpResponseRedirect("/users/login/")
    if usertype != 'Scholar':
        able = False
    if request.method == "POST":
        rawdata_path = upload_data(request,"rawdata")
        name = rawdata_path[1]
        num,datatype_suffix = divide_file(rawdata_path)
        example_path = upload_data(request,"example")
        datatype = get_datatype(datatype_suffix)
        # 解析
        taskinfo = TaskInfo()
        taskinfo.parse(request.POST, os.path.join(rawdata_path[0],rawdata_path[1]), os.path.join(example_path[0],example_path[1]), login_user, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        add_task_to_db(taskinfo,name,num,datatype)
        return render(request, 'create_task.html', {"username": login_user,"able":able})
    else:
        print request.method
        return render(request, 'create_task.html', {"username": login_user,"able":able})

def post_task(request):
    return HttpResponse("fail")

def list(request):
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    if login_user == '':
        return HttpResponseRedirect("/users/login/")
    if "load" in request.GET.keys() and request.GET["load"] == 'true':
        subject = request.GET.get("subject", None).split(' ')
        datatype = request.GET.get("datatype", None)
        print "datatype:",datatype
        order = request.GET.get("order",None)
        type = request.GET.get("type",None)
        print order
        res = get_list_from_db(subject=subject,datatype=datatype,type=type, order=order, user=scale_db_username(uno, usertype),pwd=pwd)
        return JsonResponse(res, safe=False)

    if "search" in request.GET.keys() and request.GET["search"] == 'true':
        subject = request.GET.get("subject", None).split(' ')
        datatype = request.GET.get("datatype", None)
        type = request.GET.get("type",None)
        order = request.GET.get("order", None)
        pattern = request.GET.get("pattern",None)
        isDesc = request.GET.get("isDesc",None)
        res = search(subject=subject, datatype=datatype, type=type, pattern=pattern, order=order, isDesc=isDesc, user=scale_db_username(uno, usertype), pwd=pwd)
        print res
        return JsonResponse(res, safe=False)

    return render(request, 'list.html', {"username": login_user})

def scholar_list(request):
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    if login_user == '':
        return HttpResponseRedirect("/users/login/")
    if "load" in request.GET.keys() and request.GET["load"] == 'true':
        subject = request.GET.get("subject", None).split(' ')
        datatype = request.GET.get("datatype", None)
        print "datatype:",datatype
        order = request.GET.get("order",None)
        type = request.GET.get("type",None)
        print order
        res = get_scholar_list_from_db(uno=uno, subject=subject,datatype=datatype,type=type, order=order, user=scale_db_username(uno, usertype),pwd=pwd,onlyforme=False)
        return JsonResponse(res, safe=False)

    if "search" in request.GET.keys() and request.GET["search"] == 'true':
        subject = request.GET.get("subject", None).split(' ')
        datatype = request.GET.get("datatype", None)
        type = request.GET.get("type",None)
        order = request.GET.get("order", None)
        pattern = request.GET.get("pattern",None)
        isDesc = request.GET.get("isDesc",None)
        res = search(uno=uno, subject=subject, datatype=datatype, type=type, pattern=pattern, order=order, isDesc=isDesc, user=scale_db_username(uno, usertype), pwd=pwd)
        print res
        return JsonResponse(res, safe=False)

    return render(request, 'scholar_list.html', {"username": login_user})

def manage_survey(request):
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    access = ''
    able = True
    if login_user == '':
        return HttpResponseRedirect("/users/login/")
    if request.method == 'GET':
        sno = request.GET.get("sno",-1)
        sno = int(sno)
        summary = load_summary_management(sno)
        if sno == -1:
            return HttpResponse("Survey error")
        #check authorization
        if not check_authorization(uno,sno,['OWNER','COOPERATOR']):
            if summary['stage'] == 'OPEN' or summary['publicity'] == u'私有':
                able = False
        if check_authorization(uno,sno,['OWNER']):
            access = 'OWNER'
        if "load_contributor" in request.GET.keys():
            json = load_contributor(sno)
            print json
            return JsonResponse(json,safe = False)
        if "load_by_user" in request.GET.keys():
            sa = SurveyAnswer()
            json = sa.to_json_list_by_user(sno)
            print json
            return JsonResponse(json,safe=False)
        if "load_summary" in request.GET.keys():
            print summary
            return JsonResponse(summary,safe=False)
        if "delete_id" in request.GET.keys():
            tuno =  int(request.GET['delete_id'][1:])
            delete_answer(tuno,sno)
            return HttpResponse("Success")
        if "search_user" in request.GET.keys():
            name = request.GET['name']
            json = search_scholar_by_name(name)
            print json
            return JsonResponse(json,safe = False)
        if "add_contributor" in request.GET.keys():
            uno = int(request.GET['uno'])
            add_contributor(uno,sno)
        if "close" in request.GET.keys():
            #注意：这里仅针对了调研
            publicity = request.GET['publicity'].replace(",","")
            print publicity
            if check_authorization(uno,sno,['OWNER']):
                close_survey(sno,publicity)
                return HttpResponse("修改成功")
        if "delete" in request.GET.keys():
            if check_authorization(uno, sno, ['OWNER']):
                delete_survey(sno)
                return HttpResponse("修改成功")
        if "load_date_number" in request.GET.keys():
            json = load_date_number(sno)
            print json
            return JsonResponse(json, safe=False)
        if "load_gender" in request.GET.keys():
            json = load_gender(sno)
            print "gender:",json
            return JsonResponse(json, safe=False)
        if "load_location" in request.GET.keys():
            json = load_location(sno)
            print "location:",json
            return JsonResponse(json, safe=False)

        return render(request,'manage_survey.html',{'username':login_user,'sno':sno,'access':access,'able':able})
