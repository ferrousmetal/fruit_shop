from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/',include("user.urls",namespace="user")),
    path('order/',include("order.urls",namespace="order")),
    path('cart/',include("cart.urls",namespace="cart")),
    path('',include("goods.urls",namespace="goods")),
]
