# Email Tracker
This software allows sending a mass email and tracking each time a recipient opens that email.

NOTE: Access to an SMTP server is required to use this software.

## Setup
Run the following commands to setup a local environment with the email tracker

``` sh
git clone https://github.com/willingham/email-tracker.git
cd email-tracker/
virtualenv -p python3 .
source bin/activate
pip install -r requirements.txt
python src/manage.py migrate         # sets up the DB
python src/manage.py createsuperuser # follow the prompts
```
Before you can actually send an email, you will need to configure an SMTP server in the settings.

You should create a file with the path src/emailTracker/settings/sensitive_vars.py with the following content:
``` python
SMTP_USER = 'myemail@example.com'
SMTP_PASS = 'mypassword'
```
Now, run the development server using the following command:
``` sh
python src/manage.py runserver
```

You should now be able to access the email-tracker at http://localhost:8000.



