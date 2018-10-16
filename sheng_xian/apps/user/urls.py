from django.urls import path
#导入装饰器login_required有些页面在没有登陆的情况下不能直接访问，加装饰器限制
#在访问视图函数之前加装饰器，所以可以在访问URL的时候直接加装饰器
from django.contrib.auth.decorators import login_required
app_name="user"

from apps.user.views import RegisterView,ActiveView,LoginView,UserAddressView,UserInfoView,UserOrderView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('active/<token>/',ActiveView.as_view(),name="active"),
    path('login/',LoginView.as_view(),name="login"),
    path('',login_required(UserInfoView.as_view()),name="user"),
    path('order/',login_required(UserOrderView.as_view()),name="order"),
    path('address/',login_required(UserAddressView.as_view()),name="address"),
]