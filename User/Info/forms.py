from django import forms
from .models import Student

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'event', 'visitor_type', 'phone_number', 'college_name', 'UID', 'college_id_card']

class IdUploadForm(forms.Form):
    image = forms.ImageField()
# Compare this snippet from User/Info/ocr_api.py: