from django.db import models
from django.contrib.auth.models import(
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import render, redirect
from django.http import HttpResponse


class BaseMeta(models.Model):
    create_at = models.DateTimeField(default=timezone.datetime.now)
    update_at = models.DateTimeField(default=timezone.datetime.now)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Emailは必須です')
        user = self.model(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin, BaseMeta):
    class Meta:
        verbose_name_plural = 'ユーザ'

    username = models.CharField(max_length=50)
    email = models.EmailField(max_length=255, unique=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy('student:regist')

    def __str__(self):
        return str(self.username)


class Student(BaseMeta):

    relatedUser = models.OneToOneField(
        'User', on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='ユーザ名'
    )
  

    classGroup = models.ForeignKey(
        'ClassGroup', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='所属クラス'
    )

    def __str__(self):
        return str(self.relatedUser)

    class Meta:
        verbose_name_plural = '生徒'


class Teacher(BaseMeta):
    relatedUser = models.OneToOneField(
        'User', on_delete=models.CASCADE,
        primary_key=True
    )

    def __str__(self):
        return str(self.relatedUser)

    class Meta:
        verbose_name_plural = '教師'


class ClassGroup(BaseMeta):
    className = models.CharField(max_length=50)

    teacher = models.ForeignKey(
        'Teacher', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return str(self.className)

    class Meta:
        verbose_name_plural = 'クラス'
        ordering = ('className',)


class Audio(BaseMeta):
    whichStudent = models.ForeignKey(
        'Student', on_delete=models.SET_NULL, null=True, blank=True
    )
    whichExamGr = models.ForeignKey(
        'ExamGroup', on_delete=models.SET_NULL, null=True, blank=True
    )
    whichExam = models.ForeignKey(
        'Exam', on_delete=models.SET_NULL, null=True, blank=True
    )
    whichResult = models.ForeignKey(
        'ExamResult', on_delete=models.SET_NULL, null=True, blank=True
    )
    url = models.URLField(max_length=255)

    audioFile = models.FileField()
    questionNumber = models.CharField(max_length=50)


class ExamGroup(BaseMeta):
    examGroupName = models.CharField(max_length=50)
    # urlSlug = models.SlugField(max_length=50)
    enable = models.BooleanField(default=True)
    repeatable = models.BooleanField(default=False)
    relatedExam = models.ForeignKey(
        'Exam', on_delete=models.SET_NULL, null=True, blank=True
    )
    available_class = models.ManyToManyField(ClassGroup)

    def __str__(self):
        return str(self.examGroupName)

    class Meta:
        verbose_name_plural = '試験グループ'
        ordering = ('examGroupName',)


class Exam(BaseMeta):
    examName = models.CharField(max_length=50)
    urlSlug = models.SlugField(max_length=50)
    evalBasement = models.TextField(max_length=20000)

    def __str__(self):
        return str(self.examName)

    class Meta:
        verbose_name_plural = '試験'


class ExamResult(BaseMeta):
    whosReslut = models.ForeignKey(
        'Student', on_delete=models.SET_NULL, null=True, blank=True
    )
    evalResult = models.TextField(max_length=20000)
    whichAudio = models.ForeignKey(
        'Audio', on_delete=models.SET_NULL, null=True, blank=True
    )
    whichExamGr = models.ForeignKey(
        'ExamGroup', on_delete=models.SET_NULL, null=True, blank=True
    )
    whichExam = models.ForeignKey(
        'Exam', on_delete=models.SET_NULL, null=True, blank=True
    )
    questionNum = models.CharField(max_length=50)

    def __str__(self):
        return str(self.whosReslut)

    class Meta:
        verbose_name_plural = '評価結果'


class ExamSubmit(BaseMeta):
    submited = models.BooleanField(default=False)
    whichStudent = models.ForeignKey(
        'Student', on_delete=models.SET_NULL, null=True, blank=True
    )
    whichExamGr = models.ForeignKey(
        'ExamGroup', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return str(self.submited)


class EvalRecord(BaseMeta):
    who = models.ForeignKey(
        'Teacher', on_delete=models.SET_NULL, null=True, blank=True
    )
