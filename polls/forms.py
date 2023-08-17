from django import forms
from .models import Question, Choice
from django.forms import inlineformset_factory

class AnswerChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']

AnswerChoiceFormSet = inlineformset_factory(
    Question, Choice, form=AnswerChoiceForm, extra=4  # Adjust extra as needed
)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']