from django.db import models
from django.utils import timezone

# Create your models here.

class Email(models.Model):
    reply_to = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=500, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    send_date = models.DateTimeField(default=timezone.now, blank=True)
    recipients = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=64, blank=True)
    send_now = models.BooleanField(default=True, blank=True)
    number_recipients = models.IntegerField(default=0, blank=True)
    number_sent = models.IntegerField(default=0, blank=True)
    active = models.BooleanField(default=True, blank=True)

    def __str__(self):
        return str(self.send_date) + '-' + self.subject

    class Meta:
        ordering = ('-send_date',)


class Activity(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='open', blank=True)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    recipient = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.status + '-' + self.recipient


def getUniqueActivity():
    a = Activity.objects.order_by('time').values_list('email__uuid', 'status', 'recipient').distinct()
    print('ALL: ', Activity.objects.count())
    print('UNI: ', a.count())
    return a

