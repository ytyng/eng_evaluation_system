import ast
import urllib.request
from django.urls import reverse
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView
from django import forms
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from teacher.views import *

# Audio 保存
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


class indexView(ListView):
    model = ExamGroup
    template_name = 'student/index.html'

    def get_queryset(self):
        qs = super(indexView, self).get_queryset()

        param = self.kwargs['param']
        dic = ast.literal_eval(param)

        user = User.objects.get(id=dic['id'])
        user_id = user.id

        if bool(Student.objects.filter(relatedUser=user_id)):
            classGr = user.student.classGroup
            availableExam = ExamGroup.objects.filter(
                available_class=classGr).all
        else:
            raise Exception("error!")

        return availableExam

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        param = self.kwargs['param']

        context['user_id'] = getUserId(self)

        param = self.kwargs['param']
        dic = ast.literal_eval(param)
        user = User.objects.get(id=dic['id'])

        classGr = user.student.classGroup
        examList = ExamGroup.objects.filter(available_class=classGr)

        examlist = {}

        for exam in examList:
            examlist[exam] = bool(ExamSubmit.objects.filter(
                whichStudent=user.student, whichExamGr=exam))

        # print(context)
        context['examlist'] = examlist
        return context
        # getUserId()

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ConfirmView(TemplateView):
    model = ExamGroup
    template_name = 'student/confirm.html'
    context_object_name = 'exam_list'

    def get(self, request, **kwargs):
        context = kwargs

        param = self.kwargs['s_id']
        dic = ast.literal_eval(param)
        user = User.objects.get(id=dic['id'])
        exam = ExamGroup.objects.get(id=self.kwargs['ex_id'])
        context['exam'] = exam
        context['user_id'] = getUserId(self)

        if not bool(ExamSubmit.objects.filter(whichStudent=user.student, whichExamGr=exam)):
            return self.render_to_response(context)
        else:
            return redirect(f'student:index', param=dic)

    def post(self, request, *args, **kwargs):
        ex_id = self.kwargs['ex_id']

        param = self.kwargs['s_id']
        dic = ast.literal_eval(param)
        s_id = dic['id']

        redirect_url = reverse('student:exam')

        url = f'{s_id}/exam/{ex_id}'
        return redirect(url)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ExamView(TemplateView):
    template_name = 'exams/test.html'


class ExamTestView(FormView):
    form_class = ExamSubmitForm

    def get_template_names(self):
        ex_id = self.kwargs['ex_id']
        exam = ExamGroup.objects.filter(id=ex_id)
        fileName = exam[0].relatedExam.urlSlug
        examFileName = f'exams/{fileName}.html'
        return examFileName

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ExamTestView, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        context = kwargs

        param = self.kwargs['s_id']
        dic = ast.literal_eval(param)
        user = User.objects.get(id=dic['id'])
        exam = ExamGroup.objects.get(id=self.kwargs['ex_id'])

        if not bool(ExamSubmit.objects.filter(whichStudent=user.student, whichExamGr=exam)):
            return self.render_to_response(context)
        else:
            return redirect(f'student:index', param=dic)

    def post(self, request, **kwargs):
        print(self.kwargs)
        param = self.kwargs['s_id']
        dic = ast.literal_eval(param)
        user = User.objects.get(id=dic['id'])
        exam = ExamGroup.objects.get(id=self.kwargs['ex_id'])

        if not bool(ExamSubmit.objects.filter(whichStudent=user.student, whichExamGr=exam)):
            submit = ExamSubmit()
            submit.submited = True
            submit.whichStudent = user.student
            submit.whichExamGr = exam
            submit.save()
        else:
            raise Exception

        return redirect(f'student:done', s_id=dic, ex_id=self.kwargs['ex_id'])

    def form_valid(self, form, **kwargs):
        if form.is_valid():
            param = self.kwargs['s_id']
            dic = ast.literal_eval(param)
            user = User.objects.get(id=dic['id'])
            exam = ExamGroup.objects.get(id=self.kwargs['ex_id'])

            form.instance.whichStudent = user.student
            form.instance.whichExamGr = exam
            form.save()
            print(self.kwargs)
        return super(ExamTestView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        s_id = self.kwargs['s_id']
        ex_id = self.kwargs['ex_id']

        dic = ast.literal_eval(s_id)
        stu_id = dic['id']

        context['s_id'] = s_id
        context['ex_id'] = ex_id
        self.studentDone = {'s_id': {'id': int(stu_id)}, 'ex_id': int(ex_id)}

        success_url = reverse_lazy(f'student:done', kwargs=self.studentDone)
        return context

    def get_success_url(self, **kwargs):
        context = super().get_context_data(**kwargs)

        s_id = self.kwargs['s_id']
        ex_id = self.kwargs['ex_id']

        dic = ast.literal_eval(s_id)
        stu_id = dic['id']

        studentDone = {'s_id': {'id': int(stu_id)}, 'ex_id': int(ex_id)}

        return reverse_lazy(f'student:done', kwargs=studentDone)


class DoneView(TemplateView):
    template_name = 'student/done.html'


def upload(request):

    if request.is_ajax:
        print(data)


def TestUp(request, **kwargs):
    if request.is_ajax:
        user = request.user

        recordedAudios = request.FILES

        s_id = kwargs['s_id']
        ex_id = kwargs['ex_id']
        dic = ast.literal_eval(s_id)
        stu_id = dic['id']

        stutudent = user.student
        examGr = ExamGroup.objects.get(id=ex_id)
        exam = ExamGroup.objects.get(id=ex_id).relatedExam

        for i in recordedAudios:
            path = default_storage.save(
                f'student/{stu_id}/{ex_id}/{i}.wav', ContentFile(request.FILES[i].read()))

            tmp_file = os.path.join(settings.MEDIA_ROOT, path)

            audio = Audio.objects.create(
                whichStudent=stutudent, whichExamGr=examGr, whichExam=exam, url=path, questionNumber=i)

        print(kwargs)
        return JsonResponse({'message': '送信完了！'})


class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = RegistForm


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):

        if bool(request.user.id):
            user_id = request.user.id
            parameters = {'id': user_id}

            if bool(Student.objects.filter(relatedUser=user_id)):

                return redirect('student:index', param=parameters)
            elif bool(Teacher.objects.filter(relatedUser=user_id)):
                return redirect('teacher:index', param=parameters)
            else:
                return HttpResponse('''
                <h2>利用登録が済んでいないユーザです<h2>
                <a href="/logout"><button>ログアウト</button></a>
                ''')
        else:
            return render(request, 'login.html', {'form': LoginForm, })

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(email=email, password=password)

        if user is not None:
            login(request, user)
            user_id = user.id
            print(bool(Student.objects.filter(relatedUser=user_id)))
            print(bool(Teacher.objects.filter(relatedUser=user_id)))

            parameters = {'id': user_id}

            if bool(Student.objects.filter(relatedUser=user_id)):
                redirect_url = reverse('student:index')

                url = f'{redirect_url}{parameters}'
                return redirect(url)
            elif bool(Teacher.objects.filter(relatedUser=user_id)):
                url = f'/teacher/{parameters}'
                return redirect(url)
            else:
                return HttpResponse('''
                <h2>利用登録が済んでいないユーザです<h2>
                <a href="/logout"><button>ログアウト</button></a>
                ''')


class LogoutView(FormView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')


class Upload(CreateView):
    pass


class TeacherClassView(ListView):
    model = ClassGroup
    template_name = 'teacher/index.html'

    def get_queryset(self):
        qs = super(TeacherClassView, self).get_queryset()

        param = self.kwargs['param']
        dic = ast.literal_eval(param)

        user = User.objects.get(id=dic['id'])

        if bool(Teacher.objects.filter(relatedUser=user_id)):
            print('not Redirect_teacher')
        else:
            print('redirect_teacher')
            raise Exception("error!")

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        param = self.kwargs['param']

        dic = ast.literal_eval(param)
        user = User.objects.get(id=dic['id'])
        user_id = str(user.id).zfill(5)
        context['user_id'] = user_id
        print(context)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class notRegistView(TemplateView):
    template_name = 'student/not_registerd.html'
