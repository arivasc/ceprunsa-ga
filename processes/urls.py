from django.urls import path
from processes.processViews import ProcessListCreateView, ProcessDetailView, ProcessUserCerprunsaRelationListCreateView

urlpatterns = [
  path('processes', ProcessListCreateView.as_view(), name='processes'),
  path('processes/<int:pk>', ProcessDetailView.as_view(), name='process-detail'),
  path('process-user/<int:pk>', ProcessUserCerprunsaRelationListCreateView.as_view(), name='process-user')
]