from django.db import models


class Task(models.Model):
    PENDING = 0
    COMPLETED = 1
    STATUS_OPTIONS = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
    )
    user = models.ForeignKey('auth.user', on_delete=models.CASCADE)
    title = models.CharField(max_length=20, null=True)
    description = models.CharField(max_length=200, null=True)
    due_date = models.DateTimeField()
    status = models.IntegerField(choices=STATUS_OPTIONS, default=PENDING)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.title


class SubTask(models.Model):
    PENDING = 0
    COMPLETED = 1
    STATUS_OPTIONS = (
        (PENDING, "Pending"),
        (COMPLETED, "Completed"),
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    title = models.CharField(max_length=20, null=True)
    description = models.CharField(max_length=200, null=True)
    status = models.IntegerField(choices=STATUS_OPTIONS, default=PENDING)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.title
