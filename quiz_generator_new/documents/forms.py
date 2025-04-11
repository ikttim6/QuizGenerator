from django import forms
from .models import Document


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        ext = file.name.split('.')[-1].lower()

        if ext not in ['pdf', 'docx', 'doc', 'txt']:
            raise forms.ValidationError('Only PDF, DOCX, DOC, and TXT files are allowed.')

        return file
