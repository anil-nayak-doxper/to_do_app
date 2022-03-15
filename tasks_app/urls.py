from rest_framework import routers
from tasks_app.views import SubTaskViewset, TaskViewset


router = routers.DefaultRouter()
router.register(r'task', TaskViewset)
router.register(r'subtask', SubTaskViewset)
urlpatterns = router.urls
