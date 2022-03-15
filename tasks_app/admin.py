from django.contrib import admin

from tasks_app.models import SubTask, Task

# Register your models here.
admin.site.register(Task)
admin.site.register(SubTask)
