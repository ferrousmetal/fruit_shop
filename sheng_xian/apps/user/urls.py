from django.urls import path
app_name="user"

from apps.user.views import RegisterView,ActiveView,LoginView,UseAaddressView,UserInfoView,UserOrderView

urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),
    path('active/<token>/',ActiveView.as_view(),name="active"),
    path('login/',LoginView.as_view(),name="login"),
    path('',UserInfoView.as_view(),name="user"),
    path('order/',UserInfoView.as_view(),name="order"),
    path('address/',UserInfoView.as_view(),name="address"),
]