from django.urls import path
from processes.processViews import ProcessListCreateView, ProcessDetailView

urlpatterns = [
  path('processes', ProcessListCreateView.as_view(), name='processes'),
  path('processes/<int:pk>', ProcessDetailView.as_view(), name='process-detail'),
]