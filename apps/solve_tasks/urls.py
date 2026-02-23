from django.urls import path

from .views import SolveTaskView, GetFeedbackView, GetSolutionView

urlpatterns = [
    path('solve/', SolveTaskView.as_view(), name='solve-task'),
    path('feedback/', GetFeedbackView.as_view(), name='get-feedback'),
    path('solution/<int:task_id>/', GetSolutionView.as_view(), name='get-solution'),
]
