from django.urls import path
from processes.processViews import (
  ProcessListCreateView, ProcessDetailView,
  ProcessUserCeprunsaRelationListCreateView,
  ProcessUserCeprunsaRelationDetailView)

urlpatterns = [
  path('processes', ProcessListCreateView.as_view(), name='processes'),
  path('processes/<int:pk>', ProcessDetailView.as_view(), name='process-detail'),
  path('process-user/<int:pk>', ProcessUserCeprunsaRelationListCreateView.as_view(), name='process-user'),
  path('process-user/relation/<int:pk>', ProcessUserCeprunsaRelationDetailView.as_view(), name='process-user-relation'),
]