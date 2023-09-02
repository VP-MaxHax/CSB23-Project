from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import QuestionForm, AnswerChoiceForm, AnswerChoiceFormSet, CustomAuthenticationForm
from .models import Choice, Question, Message, User
#from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from django.db import connection
from django.utils.html import escape
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.decorators import login_required
from datetime import datetime

class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
            :5
        ]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    
def add_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        formset = AnswerChoiceFormSet(request.POST, instance=Question())

        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.pub_date = timezone.now()
            question.save()

            answer_choices = formset.save(commit=False)
            for answer_choice in answer_choices:
                answer_choice.question = question
                answer_choice.save()

            return redirect('polls:index')
    else:
        form = QuestionForm()
        formset = AnswerChoiceFormSet(instance=Question())

    return render(
        request,
        'polls/add_question.html',
        {'form': form, 'formset': formset}
    )

@csrf_exempt
def custom_sql_query(request):
    query = request.POST.get("q", "")
    if query:
        with connection.cursor() as cursor:
            
            #Fix3: injection: Enable lines 106-111. Disable lines 114-117
            #---------------------------------------------
            #search='%'
            #search+=query
            #search+='%'
            #sql_query = "SELECT id, question_text FROM polls_question WHERE question_text LIKE (%s);"
            #cursor.execute(sql_query, (search,))
            #search_results = cursor.fetchall() 
            #----------------------------------------------

            sql_query = "SELECT id, question_text FROM polls_question WHERE question_text LIKE '%" + query + "%';"
            #sql_query = query
            cursor.execute(sql_query)                       #Query exploiting the injection vulnerability below if you want to test it.
            search_results = cursor.fetchall()              #are%' UNION SELECT name, password FROM polls_user WHERE name Like '

        return render(request, "polls/index.html", {"search_results": search_results})
    else:
        return render(request, "polls/index.html", {"search_results": []})

@csrf_exempt   
def register_user(request):
    username = request.POST.get("name")
    password = request.POST.get("pass")

    if username and password:
        with connection.cursor() as cursor:
            query = 'INSERT INTO polls_user (username, password) VALUES (%s, %s);'
            cursor.execute(query, (username, password))
            user = CustomUserBackend().authenticate(request, username=username, password=password) 
            login(request, user)
            return redirect("polls:success")
    
    return render(request, "polls/register.html")


#Fix2: 2. Cryptographic Failures
#----------------------------------------------------------------------------------------
#Custom user registering above stores passwords on plain text.
#Delete it (lines 123-133) and enable the register user fuction below (lines 147-168) to enable djangos own user creation system to take over
#Also remove User from .models import (Line 9) and enable djangos own user model (Line 10)
#Lastly from mysite/settings.py remove everything below line 130
#
#
#        ##Fix5: CSRF missing.
#        ##--------------------------------------------------------------
#        ##To enable csrf protection remove the "csrf_exempt"
#@csrf_exempt
#       ##---------------------------------------------------------------
#def register_user(request):
#    if request.method == 'POST':
#        username = request.POST.get("name")
#        password = request.POST.get("pass")
#        if username and password:
#            #4. Identification and Authentication Failures (lines 156-161)
#            #---------------------------------------------------
#            #passok=True
#            #candidates = [p.strip() for p in open('candidates.txt')]
#            #for i in candidates:
#            #    if password==i:
#            #        passok=False
#            #if passok:
#            #-----------------------------------------------------
#                user = User.objects.create_user(username=username, password=password)
#                #log_event(username, "register", 1)
#                return redirect("polls:login")
#        #if username is not "":
#        #    log_event(username, "register", 0)
#    return render(request, "polls/register.html")
#-------------------------------------------------------------------------------

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist: 
            return None

def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = CustomUserBackend().authenticate(request, username=username, password=password)    
            if user is not None:
                #log_event(username, "login", 1)
                login(request, user)
                return redirect("polls:success")
        elif not form.is_valid() and form.cleaned_data["username"] is not "":
            username = form.cleaned_data["username"]
            #log_event(username, "login", 0)
    else:
        form = CustomAuthenticationForm()
    return render(request, "polls/login.html", {"form": form})

@login_required
def login_success(request):
    #raise Exception(request.user)
    return render(request, 'polls/success.html', {'user': request.user})


#Fix 1. Security Logging and Monitoring Failures.
#log_event function (lines 208-212) makes an insert into "log" log table for every login and registration attempt with an username field filled.
#Also enable the log_event calls inside register_user and user_login functions (Lines:164, 166, 167, 188, 193)
#---------------------------------------------------------------------------------
#def log_event(username, event, succesfull):
#    time = datetime.now()
#    with connection.cursor() as cursor:
#        query = 'INSERT INTO log (username, event, successfull, time) VALUES (%s, %s, %s, %s);'
#        cursor.execute(query, (username, event, succesfull, time))
#--------------------------------------------------------------------------------------