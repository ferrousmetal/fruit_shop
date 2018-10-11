from apps.user.models import *
from django.shortcuts import render,redirect
import re
from django.urls import reverse
from django.views.generic import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import HttpResponse
from django.core.mail import send_mail

class RegisterView(View):
    """注册视图"""
    def get(self,request):
        """访问注册页面"""
        return render(request,"register.html")
    def post(self,request):
        """提交注册信息"""
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        cpwd = request.POST.get("cpwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")  # 判断是否勾选阅读第三方协议

        if not all([username, password, cpwd, email]):  # all是一个迭代器，用来判断数据是否都不为空
            return render(request, "register.html", {"errmsg": "请将信息填写完整"})
        if password != cpwd:
            return render(request, "register.html", {"errmsg": "两次密码不一致"})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})
        if allow != "on":
            return render(request, "register.html", {"errmsg": "请勾选用户使用协议"})
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None
        if user:
            return render(request, "register.html", {"errmsg": "用户名已存在"})
        #注册时候需要给用户邮箱发送一份邮件，邮件要携带用户的一些参数，如用户唯一的注册ID携带在参数里，
        #但是为了安全起见要进行加密，我们要安装第三方的插件：itsdangerous，我们用到了里面的一个加密方法
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = 0
        user.save()
        serializer=Serializer(settings.SECRET_KEY,3600)#设置秘钥，我们可以用Django配置文件里的秘钥
        info={"confirm":user.id}#将用户信息存放在字典里
        secret=serializer.dumps(info)#加密用字典信息
        token=secret.decode(encoding='utf8')
        subject="天天生鲜项目信息"
        message=''
        message1="<h1>%s,欢迎你成为天天生鲜会员</h1>请点击下面链接激活账户<br/><a href='http://127.0.0.1:8000/user/active/%s'>http://127.0.0.1:8000/user/active/%s</a>"%(username,token,token)
        sender=settings.EMAIL_FROM
        receiver=[email]
        send_mail(subject,message,sender,recipient_list=receiver,html_message=message1)
        return redirect(reverse('goods:index'))

class ActiveView(View):
    """激活用户视图"""
    def get(self,request,token):
        #用户点击邮件后，会携带着之前的用户ID访问我们的激活路由，将加密的用户id捕获用token接收
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:#用异常处理来执行代码，因为链接秘钥有过期时间
           info = serializer.loads(token)#解密用户信息
           user_id=info["confirm"]
           user = User.objects.get(id=user_id)
           user.is_active=1#激活用户
           user.save()
           return redirect(reverse("user:login"))#跳转到登录页面
        except SignatureExpired as e:
            return HttpResponse("激活已经过期")

class LoginView(View):
    """登录视图"""
    def get(self,request):
        return render(request,"login.html")

