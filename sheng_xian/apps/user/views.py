from apps.user.models import *
from apps.goods.models import GoodsSKU
from django.shortcuts import render,redirect
import re
from django.urls import reverse
from django.views.generic import View
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.http import HttpResponse
from celery_task.tasks import sender_register_active_email
from django.contrib.auth import authenticate,login,logout
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection#导入第三方模块用来缓存浏览记录用你来缓存商品浏览记录

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
        sender_register_active_email.delay(email,username,token)#调用celery任务函数
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
        if "usrname" in request.COOKIES:
            username=request.COOKIES.get("username")
            checked="checked"
        else:
            username=''
            checked=''
        return render(request,"login.html", {"username":username,"checked":checked})
    def post(self,request):
        """验证登录信息"""
        username=request.POST.get("username")
        password=request.POST.get('pwd')
        user = authenticate(username=username, password=password)  # django内置的用户认证，如果数据合法发挥一个User对象
        print(user)

        if not all([username,password]):
            return render(request,"login.html",{"errmsg":"用户名或密码不能为空"})

        if user is not None:#是否认证成功
            if user.is_active==1:
                login(request,user)
                #记录登录状态，保存session
                #在没有登陆的情况下，访问有些需要登录之后才能访问的页面会自动跳转到登录页面
                # 这时候URL携带的是你之前的路径，在登录之后要返回原路径，我们可以这样做
                next_url=request.GET.get("next" ,reverse("goods:index"))#要返回的URL，如果拿不到默认返回首页
                response = redirect(next_url)
                remember=request.POST.get("remember")#获取是否勾选记住密码按钮
                if remember == "on":
                    response.set_cookie("username",username,max_age=7*24*3600)
                else:
                    return response
            else:
                return render(request, "login.html", {"errmsg": "用户还未激活请到邮箱验证"})
        else:
            return render(request,"login.html",{"errmsg":"用户名或密码错误"})

class LogoutView(View):
    """退出登录"""
    def get(self,request):
        logout(request)
        return redirect(reverse('goods:index'))


class UserInfoView(LoginRequiredMixin,View):
    """用户信息类视图"""
    def get(self,request):
        user=request.user
        address=Address.objects.get_default_address(user=user)
        con = get_redis_connection('default')#redis连接对象,default为配置文件里面的缓存配置
        history_key="hestory_%d"%user.id
        #获取浏览记录的前五个商品
        history_id=con.lrange(history_key,0,4)#我们用redis列表类型存储浏览记录缓存
        sku_list=[]
        for pro_id in history_id:
            sku=GoodsSKU.objects.get(id=pro_id)
            sku_list.append(sku)

        content= {"page":"user","address":address,"sku_list":sku_list}


        return render(request,"user_center_info.html",content)

class UserOrderView(LoginRequiredMixin,View):
    """用户订单类视图"""
    def get(self,request):
        return render(request,"user_center_order.html",{"page":"order"})

class UserAddressView(LoginRequiredMixin,View):
    """用户地址类视图"""
    def get(self,request):
        """获取用户地址页面"""
        user=request.user
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     address=None
        # 引入自定义模型管理器类的方法,解决多个类重复复使用同一段代码
        address=Address.objects.get_default_address(user=user)
        return render(request,"user_center_site.html",{"page":"address","address":address})
    def post(self,request):
        """用户提交收货地址"""
        #获取提交信息
        receiver = request.POST.get("receiver")
        addr = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        #判断提交信息
        if not all([receiver,addr,phone]):
            return render(request,"user_center_site.html",{"ermsg":"信息不完整"})
        if not re.match(r'^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}',phone):
            return render(request,"user_center_site.html",{"ermsg":"电话号码格式不正确"})
        user=request.user
        # try:
        #     address=Address.objects.get(user=user,is_default=True)
        # except Address.DoesNotExist:
        #     address=Nonee
        #引入自定义模型管理器类的方法,解决多个类重复复使用同一段代码
        address = Address.objects.get_default_address(user=user)
        if address:
            is_default=False
        else:
            is_default=True
        Address.objects.create(
                               user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default
                               )
        return redirect(reverse('user:address'))



