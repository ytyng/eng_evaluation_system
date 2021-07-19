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
from teacher.views import *

app_name = 'teacher'

urlpatterns = [
    path('<param>', ClassView.as_view(), name='index'),
    path('<t_id>/<class_id>', ClassExamView.as_view(), name='classExam'),
    path('<t_id>/<class_id>/<exGr_id>',
         ExamDetailView.as_view(), name='ExamDetail'),
    path('<t_id>/<class_id>/<exGr_id>/eval',
         ExamEvalView.as_view(), name='examEval'),
    path('<t_id>/<class_id>/<exGr_id>/done',
         ExamEvalDoneView.as_view(), name='evalDone'),
    path('<t_id>/<class_id>/<exGr_id>/eval/result',
         ExamResultView.as_view(), name='examResult'),
    path('<t_id>/<class_id>/<exGr_id>/eval/result/<s_id>',
         ExamResultDetailsView.as_view(), name='examResultDetail'),
]
