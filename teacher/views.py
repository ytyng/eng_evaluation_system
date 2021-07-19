import ast
import json
import os
import urllib.request
from . import evaluate
from django.conf import settings
from django.urls import reverse
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from django.http import HttpResponse
from student.models import *
from django.views.generic.base import TemplateView, View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, FormView
from student.forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

evalErrorMsg = {}


def getContext(self, kwargs):
    user = self.request.user
    user_id = str(user.id).zfill(5)
    classGr = ClassGroup.objects.filter(id=self.kwargs['class_id'])


def getUserId(self):
    user = self.request.user
    user_id = str(user.id).zfill(5)
    return user_id


def getClassGr(self, kwargs):
    classGr = ClassGroup.objects.filter(id=self.kwargs['class_id'])
    return classGr[0]


def getExGr(self, kwargs):
    exGr = ExamGroup.objects.filter(id=self.kwargs['exGr_id'])
    return exGr[0]


def getStudent(self, kwargs):
    user = User.objects.filter(id=self.kwargs['s_id'])
    student = user[0].student
    return student


class ClassView(ListView):
    model = ClassGroup
    template_name = 'teacher/index.html'

    def get_queryset(self):
        qs = super(ClassView, self).get_queryset()
        user = self.request.user

        orderResult = ClassGroup.objects.filter(teacher=user.teacher).all

        param = self.kwargs['param']
        dic = ast.literal_eval(param)

        return orderResult

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = self.request.user
        user_id = str(user.id).zfill(5)
        context['user_id'] = user_id
        print(context)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ClassExamView(ListView):
    model = ExamGroup
    template_name = 'teacher/exam_gr.html'

    def get_queryset(self):
        qs = super(ClassExamView, self).get_queryset()
        user = self.request.user
        classGr = ClassGroup.objects.filter(id=self.kwargs['class_id'])
        orderResult = qs.filter(available_class=classGr[0]).all

        # return orderResult
        return orderResult

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_id = str(user.id).zfill(5)
        classGr = ClassGroup.objects.filter(id=self.kwargs['class_id'])

        context['user_id'] = user_id
        context['class'] = classGr[0]
        print(context)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ExamDetailView(TemplateView):
    template_name = 'teacher/exam_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        classGr = ClassGroup.objects.filter(id=self.kwargs['class_id'])
        # getUserId
        context['user_id'] = getUserId(self)
        context['class'] = getClassGr(self, kwargs)
        context['exGr'] = getExGr(self, kwargs)

        print(context)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ExamEvalView(FormView):
    template_name = 'teacher/execute_eval.html'
    form_class = ExamEvalForm

    def get_queryset(self):
        qs = super(ExamEvalView, self).get_queryset()

        classGr = ClassGroup.objects.filter(id=self.kwargs['class_id'])

        orderResult = qs.filter(classGroup=classGr[0]).all

        return orderResult

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        classGr = getClassGr(self, kwargs)
        exGr = getExGr(self, kwargs)

        context['user_id'] = getUserId(self)
        context['class'] = classGr
        context['exGr'] = exGr

        exGr = getExGr(self, kwargs)

        is_submit = {}
        classmember = Student.objects.filter(classGroup=classGr)
        for s in classmember:
            submited = bool(ExamSubmit.objects.filter(
                whichStudent=s, whichExamGr=exGr))
            is_submit[str(s)] = submited

        context['is_submit'] = is_submit
        # print(context)
        return context

    def post(self, request, **kwargs):
        user_id = self.request.user.id
        classGr = getClassGr(self, kwargs)
        exGr = getExGr(self, kwargs)
        exam = exGr.relatedExam

        global evalErrorMsg
        evalErrorMsg = {}

        evalBase = ast.literal_eval(exam.evalBasement)

        classmember = Student.objects.filter(classGroup=classGr)

        for s in classmember:

            if bool(ExamSubmit.objects.filter(whichStudent=s, whichExamGr=exGr)):

                s_id = s.relatedUser.id

                path = f'{settings.MEDIA_ROOT}/student/{s_id}/{exGr.id}/'
                print(path)
                print(s)

                for reftext, kernel in zip(evalBase['reftext'], evalBase['kernel']):
                    if os.path.exists(f'{path}{reftext}.wav') and not ExamResult.objects.filter(whosReslut=s, whichExamGr=exGr, questionNum=reftext):
                        audio = Audio.objects.filter(
                            whichStudent=s, whichExamGr=exGr, questionNumber=kernel)
                        refText = evalBase['reftext'][reftext]
                        audioPath = f'{path}{reftext}.wav'
                        kernel = evalBase['kernel'][kernel]

                        print(audioPath)
                        print(audio)

                        resultJson = evaluate.runEval(
                            refText, audioPath, kernel)

                        json_dict = json.loads(resultJson)
                        print(f'JSONの中身確認：{json_dict}')

                        # if not bool(json_dict['error']) :
                        if not bool('error' in json_dict):
                            # JSON保存
                            result = ExamResult()
                            result.whosReslut = s
                            result.evalResult = resultJson
                            result.whichAudio = audio[0]
                            result.whichExamGr = exGr
                            result.whichExam = exam
                            result.questionNum = reftext

                            result.save()

                        else:
                            dic = {}
                            dic[s] = s
                            dic['error'] = json_dict['error']['id']
                            dic['msg'] = json_dict['error']['msg']

                            evalErrorMsg[s] = dic

                    else:
                        print('ファイルが存在しません')

        exacute = EvalRecord(who=self.request.user.teacher)
        exacute.save()

        return redirect(f'teacher:evalDone', t_id=user_id, class_id=classGr.id, exGr_id=exGr.id)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ExamEvalDoneView(TemplateView):
    template_name = 'teacher/eval_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        global evalErrorMsg

        context['msg'] = evalErrorMsg
        context['user_id'] = getUserId(self)

        return context


class ExamResultView(TemplateView):
    template_name = 'teacher/exam_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        classGr = getClassGr(self, kwargs)
        exGr = getExGr(self, kwargs)

        context['user_id'] = getUserId(self)
        context['class'] = classGr
        context['exGr'] = exGr

        exGr = getExGr(self, kwargs)

        is_result = {}
        is_submit = {}
        is_evaluated = {}
        classmember = Student.objects.filter(classGroup=classGr)
        for s in classmember:
            for s in classmember:
                dic = {}
                submited = bool(ExamSubmit.objects.filter(
                    whichStudent=s, whichExamGr=exGr))
                evaluated = bool(ExamResult.objects.filter(
                    whosReslut=s, whichExamGr=exGr))
                dic['submit'] = submited
                dic['evaluated'] = evaluated

                is_result[s] = dic

            context['is_result'] = is_result

        return context


class ExamResultDetailsView(TemplateView):
    template_name = 'teacher/eval_result_datail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        classGr = getClassGr(self, kwargs)
        exGr = getExGr(self, kwargs)
        student = getStudent(self, kwargs)

        context['user_id'] = getUserId(self)
        context['class'] = classGr
        context['exGr'] = exGr
        context['student'] = student

        exGr = getExGr(self, kwargs)

        evalResult = {}
        results = ExamResult.objects.filter(
            whosReslut=student, whichExamGr=exGr)
        print(results)
        for r in results:
            evalResult[r.questionNum] = ast.literal_eval(r.evalResult)

        context['result'] = evalResult
        return context
