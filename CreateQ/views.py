# encoding=utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
# Create your views here.
from sqls import *
from sqls_ans import *


def scale_db_username(uno, usertype):
    return 'scholar_%d' % uno if usertype == 'Scholar' else 'volunteer_%d' % uno

def get_basic_from_session(request):
    login_user = request.session.get("username", "")
    uno = int(request.session.get("uno", 0))
    pwd = request.session.get("pwd", "")
    usertype = request.session.get("usertype", "")
    return login_user,uno,pwd,usertype

def new_survey(request):
    login_user,uno,pwd,usertype = get_basic_from_session(request)
    if login_user == '':
        return HttpResponseRedirect("/users/login/")
    if usertype != 'Scholar':
        return HttpResponse('Forbidden')
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

    return render(request, 'create_survey.html', {"username": login_user})


def list_survey(request):
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    if "load" in request.GET.keys() and request.GET["load"] == 'true':
        title = request.GET.get("title", None)
        subject = request.GET.get("subject", None).split(' ')
        order = request.GET.get("order", None)
        res = get_survey_from_db(title=title, subject=subject, order=order,user=scale_db_username(uno,usertype),pwd=pwd)
        print res
        return JsonResponse(res, safe=False)

    return render(request, 'list_survey.html', {"username": login_user})


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

def manage_survey(request):
    login_user, uno, pwd, usertype = get_basic_from_session(request)
    if request.method == 'GET':
        sno = request.GET.get("sno",-1)
        sno = int(sno)
        if sno == -1:
            return HttpResponse("Survey error")
        #check authorization
        if not check_authorization(uno,sno,['OWNER']):
            return HttpResponse("You have no access for view pending answers in this survey")
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
            json = load_summary_management(sno)
            print json
            return JsonResponse(json,safe=False)
        if "delete_id" in request.GET.keys():
            tuno =  int(request.GET['delete_id'][1:])
            delete_answer(tuno,sno)
            return HttpResponse("Success")
        if "search_user" in request.GET.keys():
            name = request.GET['name']
            json = search_scholar_by_name(name)
            print json
            return JsonResponse(json,safe = False)
        return render(request,'manage_survey.html',{'username':login_user,'sno':sno})
