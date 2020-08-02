from django.urls import path
from .views import *

urlpatterns = [
    path("",signup,name='home'),
    path("signup",signup,name="signup"),
    path("login",login,name="login"),
    path("logout/",logout,name="logout"),
    path("dashboard/",dashboard,name="dashboard"),
    path("search",search,name="search"),
    path("monitor/",getMonitoring,name="monitor"),
    path("addToMonitor/",addToMonitor,name="addTomMonitor"),
    path("remove",removeItem,name="removeItem"),
    path("monitorproducts",sendmail,name="sendmail"),
    path("send",send,name="send"),
]