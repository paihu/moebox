from django import forms

class UploadFileForm(forms.Form):
    uploadfile = forms.FileField()
    delete_key = forms.CharField(max_length=1024)
    comment = forms.CharField(max_length=1024,required=False)
    secret= forms.BooleanField(required=False)
    secret_key = forms.CharField(max_length=1024,required=False)

