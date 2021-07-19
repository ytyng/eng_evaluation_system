"""evalsys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from student import views
from student.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('student/', include('student.urls')),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('', RegistUserView.as_view(), name='regist'),
    path('notregist/', notRegistView.as_view(), name='not'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('upload/', Upload.as_view(), name='up'),
    path('teacher/',  include('teacher.urls')),
]
