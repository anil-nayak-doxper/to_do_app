from rest_framework import serializers
from tasks_app.models import SubTask, Task


class SubTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubTask
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'

    def get_subtasks(self, obj):
        serializer = SubTaskSerializer(obj.subtask_set.all(), many=True)
        return serializer.data
