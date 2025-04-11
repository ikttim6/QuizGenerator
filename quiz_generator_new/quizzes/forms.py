from django import forms
from .models import Quiz, Question, Choice
from documents.models import Document


class QuizGenerationForm(forms.Form):
    document = forms.ModelChoiceField(queryset=None)
    title = forms.CharField(max_length=255)
    num_multiple_choice = forms.IntegerField(min_value=0, initial=5, label="Number of Multiple Choice Questions")
    num_true_false = forms.IntegerField(min_value=0, initial=3, label="Number of True/False Questions")
    num_essay = forms.IntegerField(min_value=0, initial=2, label="Number of Essay Questions")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['document'].queryset = Document.objects.filter(uploaded_by=user)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text', 'question_type']


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'is_correct']
