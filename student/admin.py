from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)
admin.site.register(ClassGroup)
admin.site.register(Teacher)
admin.site.register(ExamGroup)
admin.site.register(Exam)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    field = ('id''relatedUser', 'classGroup')
    list_display = ('relatedUser', 'classGroup')
    list_display_links = ('relatedUser',)
    list_editable = ('classGroup',)


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):

    field = ('whosReslut', 'whichExamGr', 'create_at')
    list_display = ('whosReslut', 'whichExamGr')
    list_display_links = ('whosReslut', 'whichExamGr')
