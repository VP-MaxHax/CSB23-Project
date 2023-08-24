from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import QuestionForm, AnswerChoiceForm, AnswerChoiceFormSet, CustomAuthenticationForm
from .models import Choice, Question, Message, User
from django.forms import inlineformset_factory
from django.db import connection
from django.utils.html import escape
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, get_user_model
#from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import BaseUserManager

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
        # Redisplay the question voting form.
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
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
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

            return redirect('polls:index')  # Redirect to a success page
    else:
        form = QuestionForm()
        formset = AnswerChoiceFormSet(instance=Question())

    return render(
        request,
        'polls/add_question.html',
        {'form': form, 'formset': formset}
    )

def custom_sql_query(request):
    query = request.GET.get("q", "")

    if query:
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        return render(request, "polls/search.html", {"results": results})
    else:
        return render(request, "polls/search.html", {"results": []})

@csrf_exempt   
def register_user(request):
    name = request.GET.get("name")
    password = request.GET.get("pass")

    if name and password:
        with connection.cursor() as cursor:
            query = 'INSERT INTO polls_user (name, password) VALUES (%s, %s);'
            cursor.execute(query, (name, password))
    
    return render(request, "polls/register.html")


#@csrf_exempt
#def register_user(request):
#    if request.method == 'POST':
#        username = request.POST.get("name")
#        password = request.POST.get("pass")
#
#        if username and password:
#            user = User.objects.create_user(username=username, password=password)
#            # You can log the user in after registration if needed
#            # auth.login(request, user)
#            return redirect("login")  # Redirect to the login page after registration
#
#    return render(request, "polls/register.html")

class CustomUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(name=username)  # Use your custom User model
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
                login(request, user)
                return redirect("polls:index")  # Redirect to home page after login
    else:
        form = CustomAuthenticationForm()
    
    return render(request, "polls/login.html", {"form": form})

