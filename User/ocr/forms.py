from django import forms
class IdUploadForm(forms.Form):
    image = forms.ImageField()