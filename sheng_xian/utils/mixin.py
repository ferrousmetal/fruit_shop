from django.contrib.auth.decorators import login_required
# 有些页面访问时需要判断是否登录，用了django内置的装饰器login_required
# 我们可以把公用的方法抽取出来重用，不用在每个类视图视图中加同样的装饰器，可以用到多继承，
# 在多继承中，有优先级，优先继承排在前面的类，所以会优先执行这个装饰器类，
# 让每个需要这个装饰器类优先继承它


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls,**initkwards):
        view = super(LoginRequiredMixin,cls).as_view(**initkwards)
        return login_required(view)


