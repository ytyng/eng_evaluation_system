from django import forms
from .models import *
from django.shortcuts import redirect
from django.http import HttpResponse

# from django.contrib.auth.password_validation import validate_password


class RegistForm(forms.ModelForm):
    username = forms.CharField(label="名前")
    email = forms.EmailField(label="メールアドレス")
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=False):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()

        return user

    def __init__(self, *args, **kwargs):
        super(RegistForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label


class LoginForm(forms.Form):
    email = forms.EmailField(label="メールアドレス")
    password = forms.CharField(label="パスワード", widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label


class StartExamForm(forms.Form):
    user_id = forms.IntegerField()
    exam_id = forms.IntegerField()


class ExamSubmitForm(forms.ModelForm):
    submited = forms.BooleanField()

    class Meta:
        model = ExamSubmit
        fields = ('submited',)


class ExamEvalForm(forms.ModelForm):

    class Meta:
        model = EvalRecord
        fields = ('who',)
