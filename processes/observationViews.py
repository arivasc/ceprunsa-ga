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
    summary='Listar observaciones',
    description="Listado de observaciones de los usuarios en todos los procesos."
                "\n\nPara filtrar por ID de la relación de usuario y proceso, se"
                " debe enviar el parámetro idProcessUserCeprunsaRelation en la URL"
                " con el campo a filtrar idProcessUserCeprunsaRelation=id.",
    responses=ObservationDetailSerializer(many=True),
    parameters=[
      OpenApiParameter(
        name='idProcessUserCeprunsaRelation',
        required=False,
        description='ID de idProcessUserCeprunsaRelation',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='idProcessUserCeprunsaRelation',
            value='1'
          )
        ]
      )
    ]
  )
  def get(self, request):
    idProcessUserCeprunsaRelation = request.query_params.get('idProcessUserCeprunsaRelation', None)
        
    if idProcessUserCeprunsaRelation:
      try:
        observations = Observation.objects.filter(idProcessUserCeprunsaRelation=idProcessUserCeprunsaRelation)
      except ObjectDoesNotExist:
        return Response({'message': 'No se encontraron observaciones con ese id.'}, status=status.HTTP_404_NOT_FOUND)
    else:
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