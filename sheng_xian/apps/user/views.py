from apps.user.models import *
from django.shortcuts import render,redirect
import re
from django.urls import reverse
# Create your views here.

def register(request):
    return  render(request,"register.html")

def register_handle(request):
    username=request.POST.get("user_name")
    password=request.POST.get("pwd")
    cpwd=request.POST.get("cpwd")
    email=request.POST.get("email")
    allow = request.POST.get("allow")#判断是否勾选阅读第三方协议
    if request.method=="POST":
        if not all([username,password,cpwd,email,allow]):#all是一个迭代器，用来判断数据是否都不为空
            return render(request,"register.html",{"errmsg":"请将信息填写完整"})
        if password!=cpwd:
            return render(request,"register.html",{"errmsg":"两次密码不一致"})
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})
        if allow!="on":
            return render(request, "register.html", {"errmsg": "请勾选用户使用协议"})
        try:
           user=User.objects.get(username=username)
        except User.DoesNotExist:
            user=None
        if user:
            return render(request, "register.html", {"errmsg": "用户名已存在"})

        user=User.objects.create_user(username=username,email=email,password=password)
        user.is_active=0
        user.save()
        return redirect(reverse('goods:index'))
