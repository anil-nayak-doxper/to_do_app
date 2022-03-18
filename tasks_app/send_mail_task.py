
from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from apscheduler.schedulers.background import BackgroundScheduler
from tasks_app.models import Task 


def schedule_send_email_task(title):
    task = Task.objects.get(title=title)
    subject = 'Reminder for your task'
    body = 'Your due_time is nearing. Try to complete the task before due_time.'
    mail_from = settings.EMAIL_HOST_USER
    receipient = task.user.email
    remind_time = task.due_date - timedelta(minutes=task.reminder*60)
    args = [subject,body,mail_from,[receipient]]
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_mail,'date',run_date=remind_time,args=args)
    scheduler.start()

