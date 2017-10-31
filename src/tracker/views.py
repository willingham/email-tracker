from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
import datetime
import time
from django.utils.dateparse import parse_datetime

from .forms import EmailModelForm
from .models import Email, Activity, getUniqueActivity
import bs4, smtplib
import uuid as uid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import logging

logger = logging.getLogger('django')

# Create your views here.


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'tracker/home.html'

    def get_context_data(self, **kwargs):
        c = super(HomeView, self).get_context_data(**kwargs)
        emails = Email.objects.all()
        c['emails_all'] = emails
        c['emails_active'] = emails.filter(active=True)

        totalOpenByHour = Activity.objects.filter(email__active=True, status='open').extra({'day-hour': 'strftime("%%m-%%d Hour %%H", time)'}).order_by().values('day-hour').annotate(count=Count('id'))
        activityHours = []
        activityLevel = []
        activityLevelMax = 0
        for item in totalOpenByHour:
            count = item['count']
            activityHours.append(item['day-hour'])
            activityLevel.append(count)
            if count > activityLevelMax:
                activityLevelMax = count

        allActivity = Activity.objects.order_by('-time')
        uniqueOpensParse = {}
        for a in allActivity:
            if a.email.uuid in uniqueOpensParse.keys():
                uniqueOpensParse[a.email.uuid][a.recipient] = a.time
            else:
                uniqueOpensParse[a.email.uuid] = { a.recipient: a.time }

        uniqueOpens = {}
        for uuid in uniqueOpensParse.keys():
            uniqueOpens[uuid] = []
            for email in uniqueOpensParse[uuid].keys():
                uniqueOpens[uuid].append([email, uniqueOpensParse[uuid][email]])
        print("Unique opens 2", uniqueOpens)


        print("Unique opens: ", uniqueOpens.keys())

        uniqueOpensForGraph = []
        for hour in activityHours:
            totalUnique = 0
            for uuid in uniqueOpens.keys():
                for open in uniqueOpens[uuid]:
                    date = parse_datetime(str(open[1]))
                    print(date, hour)
                    if date.strftime("%m-%d Hour %H") == hour:
                        totalUnique += 1
            uniqueOpensForGraph.append(totalUnique)

        print("UniqueOpensForGraph: ", uniqueOpensForGraph)




        c['uniqueOpens'] = uniqueOpens
        c['uniqueOpensForGraph'] = uniqueOpensForGraph

        c['totalOpenByHour'] = totalOpenByHour
        c['activity'] = Activity.objects.all()
        c['activityHours'] = str(activityHours)
        c['activityLevel'] = str(activityLevel)
        c['activityLevelMax'] = activityLevelMax + 1
        u = getUniqueActivity()
        d3 = []
        print(type(activityHours))
        for i in range(len(activityHours)):
            temp = {}
            temp['hour'] = activityHours[i]
            temp['total'] = activityLevel[i]
            temp['unique'] = uniqueOpensForGraph[i]
            d3.append(temp)
        #d3.append({'hour': '09-24 Hour 21', 'total': 18, 'unique': 2})
        #d3.append({'hour': '09-24 Hour 22', 'total': 3, 'unique': 3})
        c['d3list'] = str(d3)

        print("activityHours", c['activityHours'])
        return c


def getSMTPConnection():
    u = getattr(settings, "SMTP_USER", None)
    p = getattr(settings, "SMTP_PASS", None)
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(u, p)

    return server, u


def SMTPIsActive(con):
    try:
        status = con.noop()[0]
    except:  # smtplib.SMTPServerDisconnected
        status = -1
    return True if status == 250 else False


def formatHtml(event, uuid, body, recipient):
        domain = getattr(settings, "EVENT_DOMAIN", None)
        url = "{domain}/event/{uuid}/{event}/{to}/"
        url = url.format(domain=domain, event=event, uuid=uuid, to=recipient)
        html = bs4.BeautifulSoup(body, 'html.parser')

        # Open tracker
        openTracker = html.new_tag('img', src=url)
        html.body.append(openTracker)

        return str(html)



def getMIME(from_addr, reply, subject, event, uuid, body, recipient):
    html = formatHtml(event, uuid, body, recipient)
    msg = MIMEMultipart('alternative')
    msg['From'] = from_addr
    msg['To'] = recipient
    msg['Subject'] = subject
    htmlPart = MIMEText(html, 'html')
    msg.add_header('reply-to', reply)
    msg.attach(htmlPart)

    return msg


class SendMessagesThread(threading.Thread):
    def __init__(self, recipients, reply_to, subject, uuid, body, *args, **kwargs):
        self.recipients = recipients
        self.reply_to = reply_to
        self.subject = subject
        self.uuid = uuid
        self.body = body
        super(SendMessagesThread, self).__init__(*args, **kwargs)

    def run(self):
        sendMessages(self.recipients, self.reply_to, self.subject, self.uuid, self.body)


def sendMessages(recipients, reply_to, subject, uuid, body):
    number_sent = 0
    try:
        con, f = getSMTPConnection()
        print("Connection:", con)
        print("F:", f)
        while (len(recipients)) > 0:
            error = 0
            recipient = recipients.pop()
            try:
                msg = getMIME(f, reply_to, subject, "open", uuid, body, recipient)
                number_sent += 1
                con.sendmail(f, [recipient], msg.as_string())
            except Exception as e:
                #print(e)
                number_sent -= 1
                if not SMTPIsActive(con):
                    print("         : inactive")
                    con, f = getSMTPConnection()
                recipients.append(recipient)
            if error:
                print("Recipient [ERR]:", recipient)
                logger.info("Recipient [ERR]:" + recipient)
            else:
                print("Recipient [" + str(number_sent) + "]:", recipient)
                logger.info("Recipient [" + str(number_sent) + "]:" + recipient)

        messages.success(self.request, "Sent {} messages.".format(number_sent))
    except:
        messages.warning(self.request, "Couldn't send messages!  Try again.")
    Email.objects.filter(uuid=uuid).update(number_sent=number_sent)


class EmailCreateView(LoginRequiredMixin, CreateView):
    form_class = EmailModelForm
    template_name = 'tracker/email-create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        subject = form.cleaned_data.get('subject')
        body = "<body>" + form.cleaned_data.get('body') + "</body>"
        recipients_orig = form.cleaned_data.get('recipients')
        recipients = recipients_orig.splitlines()
        reply_to = form.cleaned_data.get('reply_to')
        uuid = str(uid.uuid4())
        form.instance.uuid = uuid
        form.instance.body = body
        form.instance.number_recipients = len(recipients)
        form.instance.number_sent = -1
        send_now = form.cleaned_data.get('send_now')
        print("uuid: ", uuid)

        messages.success(self.request, "Added email: {}".format(subject))
        print("send_now: ",send_now)
        if send_now:
            SendMessagesThread(recipients, reply_to, subject, uuid, body).start()


        return super(EmailCreateView, self).form_valid(form)


def eventView(request, uuid, event, recipient):
    print(uuid, event, recipient)
    email = Email.objects.filter(uuid=uuid).first()

    if email:
        a = Activity(email=email, status=event, recipient=recipient)
        a.save()

    return HttpResponse('')

