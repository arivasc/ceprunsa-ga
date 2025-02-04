from processes.serializers import ObservationSerializer, ObservationDetailSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from processes.models import Observation

#===============================================================
# ObservationView para crear y listar observaciones
#===============================================================
class ObservationListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    description='Listado de observaciones',
    responses=ObservationDetailSerializer(many=True),
    parameters=[
      OpenApiParameter(
        name='idProcessUserCeprunsaRelation',
        required=False,
        description='ID de la relación de usuario y proceso',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='Ejemplo 1',
            value='1'
          )
        ]
      )
    ]
  )
  def get(self, request):
    observations = Observation.objects.all()
    serializer = ObservationDetailSerializer(observations, many=True)
    return Response(serializer.data)
  
  @extend_schema(
    description='Crear una observación',
    request=ObservationSerializer,
    responses=ObservationSerializer
  )
  def post(self, request):
    serializer = ObservationSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)