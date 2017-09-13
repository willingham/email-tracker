from django import forms
from .models import Email, Activity

class EmailModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailModelForm, self).__init__(*args, **kwargs)
        self.fields['uuid'].disabled = True
        self.fields['uuid'].widget.attrs['size'] = 36

    class Meta:
        model = Email
        exclude = ['number_sent', 'from_address']