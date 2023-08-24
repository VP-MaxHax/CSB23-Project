from django import forms
from .models import Question, Choice
from django.forms import inlineformset_factory
from django.contrib.auth.forms import AuthenticationForm

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

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))