from django.urls import path
from processes.processViews import (
  ProcessListCreateView, ProcessDetailView,
  ProcessUserCeprunsaRelationListCreateView,
  ProcessUserCeprunsaRelationDetailView,
  ProcessStateChangeView,
  ProcessUserCeprunsaListView)

from processes.observationViews import ObservationListCreateView, ObservationDetailEditView, ObservationDocumentView

urlpatterns = [
  path('processes', ProcessListCreateView.as_view(), name='processes'),
  path('processes/<int:pk>', ProcessDetailView.as_view(), name='process-detail'),
  path('processes/change-state/<int:pk>', ProcessStateChangeView.as_view(), name='process-change-state'),
  path('process-user/<int:pk>', ProcessUserCeprunsaRelationListCreateView.as_view(), name='process-user'),
  path('process-user/relation/<int:pk>', ProcessUserCeprunsaRelationDetailView.as_view(), name='process-user-relation'),
  path('process-user/history/<int:pk>', ProcessUserCeprunsaListView.as_view(), name='process-user-ceprunsa'),
  path('observations', ObservationListCreateView.as_view(), name='observations'),
  path('observations/<int:pk>', ObservationDetailEditView.as_view(), name='observation-detail'),
  path('observations/document/<int:pk>', ObservationDocumentView.as_view(), name='observation-document'),
]