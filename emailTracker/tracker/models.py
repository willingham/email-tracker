from django.db import models
import uuid

# Create your models here.

class Email(models.Model):
    from_address = models.EmailField(null=True, blank=True)
    reply_to = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=500, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    send_date = models.DateTimeField(auto_now_add=True, blank=True)
    recipients = models.TextField(null=True, blank=True)
    uuid = models.CharField(max_length=64, default=uuid.uuid1, blank=True)
    send_now = models.BooleanField(default=True, blank=True)
    number_sent = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return str(self.send_date) + '-' + self.subject

    class Meta:
        ordering = ('-send_date',)


class Activity(models.Model):
    email = models.ForeignKey(Email, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='opened', blank=True)
    time = models.DateTimeField(auto_now_add=True, blank=True)
    recipient = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.status + '-' + self.recipient
