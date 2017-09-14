from django import forms
from .models import Email, Activity
#import uuid

class EmailModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailModelForm, self).__init__(*args, **kwargs)
        #self.fields['uuid'].disabled = True
        #self.fields['uuid'].widget.attrs['size'] = 40
        #u = str(uuid.uuid4())
        #self.fields['uuid'].initial = u

    class Meta:
        model = Email
        exclude = ['number_sent', 'from_address', 'uuid']