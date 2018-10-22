from django.conf import settings
from celery import Celery
from django.core.mail import send_mail
import time

#传建一个celery的实例对象
app=Celery('celery_task.tasks',broker="redis://192.168.2.106/8")

#定义celery任务函数
@app.task
def sender_register_active_email(to_email,username,token):
    """发送激活邮件"""
    subject = "天天生鲜项目信息"
    message = ''
    message1 = "<h1>%s,欢迎你成为天天生鲜会员</h1>请点击下面链接激活账户<br/><a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>" % (
    username, token, token)
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    send_mail(subject, message, sender, recipient_list=receiver, html_message=message1)
    time.sleep(5)