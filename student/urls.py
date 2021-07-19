from django.urls import path
from . import views
from .views import *

app_name = 'student'

urlpatterns = [
    path('', indexView.as_view(), name='index'),
    path('<param>', indexView.as_view(), name='index'),
    path('regist/', RegistUserView.as_view(), name='regist'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('<s_id>/confirm/<ex_id>', ConfirmView.as_view(), name='confirm'),
    path('<s_id>/exam/<ex_id>', ExamView.as_view(), name='exam'),
    path('<s_id>/confirm/<ex_id>/exam', ExamTestView.as_view(), name='examtest'),
    path('<s_id>/confirm/<ex_id>/done', DoneView.as_view(), name='done'),
    path('<s_id>/confirm/<ex_id>/upload/', views.upload, name='up'),
    path('<s_id>/confirm/<ex_id>/exam/testup/', views.TestUp, name='testup'),
]