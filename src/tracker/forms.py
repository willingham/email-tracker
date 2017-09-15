from django import forms
from .models import Email, Activity
#import uuid

class EmailModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailModelForm, self).__init__(*args, **kwargs)
        self.fields['reply_to'].widget.attrs['class'] = 'form-control'
        self.fields['subject'].widget.attrs['class'] = 'form-control'
        self.fields['recipients'].widget.attrs['class'] = 'form-control'
        self.fields['send_now'].widget.attrs['class'] = 'form-control'
        self.fields['active'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Email
        exclude = ['number_sent', 'from_address', 'uuid', 'send_date']