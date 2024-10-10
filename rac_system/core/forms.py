from django import forms

class UploadCSVForm(forms.Form):
    expert_csv = forms.FileField(label="Upload Expert CSV")
    candidate_csv = forms.FileField(label="Upload Candidate CSV")
