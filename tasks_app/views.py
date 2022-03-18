
from datetime import datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from tasks_app.models import SubTask, Task
from tasks_app.send_mail_task import schedule_send_email_task
from tasks_app.serializers import SubTaskSerializer, TaskSerializer


class TaskViewset(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def list(self, request, *args, **kwargs):
        title = request.GET.get('title', None)
        if title:
            self.queryset = self.queryset.filter(title=title)
        serializer = TaskSerializer(
            Task.objects.filter(user=request.user), many=True)
        return Response(serializer.data,  status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        title = data.get('title', '')
        description = data.get('description', '')
        due_date = data.get('due_date', '')
        reminder = data.get('reminder', -1)
        if due_date:
            due_date = datetime.strptime(due_date, "%Y-%m-%d")
        else:
            due_date = datetime.today()+timedelta(days=5)
        if reminder == -1:
            reminder = 4
        if not title:
            return Response({'error': 'Title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if Task.objects.filter(title=title).exists():
            return Response({'error': 'task with same title already exists'}, status=status.HTTP_400_BAD_REQUEST)
        task_data = {'user': request.user.id, 'title': title,
                     'description': description, 'due_date': due_date, 'reminder': reminder}
        serializer = TaskSerializer(data=task_data)
        if serializer.is_valid():
            serializer.save()
            schedule_send_email_task(title)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        data = request.data.copy()
        task_id = data.get('id', '')
        task_title = data.get('title', '')
        if not task_id and not task_title:
            return Response({'error': 'task_id or task_title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if task_id:
            task = Task.objects.get(id=task_id)
        elif task_title:
            task = Task.objects.get(title=task_title)
        if not task:
            return Response({'error': 'Invalid task_id'}, status=status.HTTP_400_BAD_REQUEST)
        if task.user != request.user:
            return Response({'error': 'You are not allowed'}, status=status.HTTP_401_UNAUTHORIZED)
        is_completed = data.get('is_completed', False)
        description = data.get('description', '')
        if not description:
            description = task.description
        task_status = task.status
        if is_completed:
            task_status = Task.COMPLETED
        task.description = description
        task.status = task_status
        task.save()
        if task_status == Task.COMPLETED:
            subtasks = SubTask.objects.filter(task=task)
            for item in subtasks:
                item.status = task_status
                item.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)


class SubTaskViewset(viewsets.ModelViewSet):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer

    def list(self, request, *args, **kwargs):
        task_id = request.GET.get('task_id', '')
        subtask_id = request.GET.get('subtask_id', '')
        task_title = request.GET.get('task_title', '')
        subtask_title = request.GET.get('subtask_title', '')

        if subtask_id:
            self.queryset = self.queryset.filter(id=subtask_id)
        elif subtask_title:
            self.queryset = self.queryset.filter(title=subtask_title)
        elif task_id:
            self.queryset = self.queryset.filter(task_id=task_id)
        elif task_title:
            self.queryset = self.queryset.filter(task__title=task_title)

        if self.queryset and request.user != self.queryset[0].task.user:
            return Response({'error': 'You are not allowed'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SubTaskSerializer(self.queryset, many=True)
        return Response(serializer.data,  status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        data = request.data.copy()
        subtask_id = data.get('id', '')
        subtask_title = data.get('title', '')
        if not subtask_id and not subtask_title:
            return Response({'error': 'id or title is required'}, status=status.HTTP_400_BAD_REQUEST)
        if subtask_id:
            subtask = SubTask.objects.get(id=subtask_id)
        elif subtask_title:
            subtask = SubTask.objects.get(title=subtask_title)
        if not subtask:
            return Response({'error': 'Invalid task_id'}, status=status.HTTP_400_BAD_REQUEST)
        is_completed = data.get('is_completed', False)
        description = data.get('description', '')
        if not description:
            description = subtask.description
        task_status = subtask.status
        if is_completed:
            task_status = Task.COMPLETED
        subtask.description = description
        subtask.status = task_status
        subtask.save()
        return Response(SubTaskSerializer(subtask).data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        task_id = data.get('task_id', '')
        task_title = data.get('task_title', '')
        if not task_id and not task_title:
            return Response({'error': 'id or title of task is required'}, status=status.HTTP_400_BAD_REQUEST)
        task = None
        if task_id:
            task = Task.objects.get(id=task_id)
        elif task_title:
            task = Task.objects.get(title=task_title)
        if not task:
            return Response({'error': 'Invalid task_id'}, status=status.HTTP_400_BAD_REQUEST)
        elif request.user != task.user:
            return Response({'error': 'You are not allowed'}, status=status.HTTP_401_UNAUTHORIZED)
        title = data.get('title', '')
        description = data.get('description', '')
        due_date = data.get('due_date', '')
        if due_date:
            due_date = datetime.strptime(due_date, "%Y-%m-%d")
        else:
            due_date = datetime.today()+timedelta(days=5)
        if not title:
            return Response({'error': 'Title for subtask is required'}, status=status.HTTP_400_BAD_REQUEST)
        if SubTask.objects.filter(title=title).exists():
            return Response({'error': 'Subtask with same title already exists'}, status=status.HTTP_400_BAD_REQUEST)
        subtask_data = {'task': task.id, 'title': title,
                        'description': description, 'due_date': due_date}
        serializer = SubTaskSerializer(data=subtask_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
