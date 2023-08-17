from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .forms import QuestionForm, AnswerChoiceForm, AnswerChoiceFormSet
from .models import Choice, Question
from django.forms import inlineformset_factory

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