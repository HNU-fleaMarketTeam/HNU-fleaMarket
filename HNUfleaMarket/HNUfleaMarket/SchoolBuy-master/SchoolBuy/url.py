from django.conf.urls import url
from SchoolBuy.views import *

urlpatterns = (url(r'^create_code/$', create_code_img),  # 生成验证码
               url(r'^$', home),
               url(r'^register/$', register),  # 注册
               url(r'^login/$', login),  # 登录
               url(r'^logout/$', logout),  # 登出
               url(r'^push_goods/$', push_goods),  #发布商品
               url(r'^goods/(?P<number>\d+)/$', look_goods),  # 浏览id商品
               url(r'^all/$',goods_list),  # 浏览所有商品
