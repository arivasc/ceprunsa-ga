from processes.serializers import ObservationSerializer, ObservationDetailSerializer, ObservationDocumentUrlSerializer

from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from processes.models import Observation

#===============================================================
# ObservationDocumentView para ver el documento de la observación
#===============================================================
class ObservationDocumentView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary='Ver el documento de una observación',
    description='Ver el documento de una observación por su ID.',
    responses={200: None}
  )
  def get(self, request, pk):
    try:
      observation = Observation.objects.get(pk=pk)
      if observation.document:
        serializer = ObservationDocumentUrlSerializer(observation)
        return Response(serializer.data, status=status.HTTP_200_OK)
      else:
        return Response({'message': 'No hay documento asociado a esta observación.'}, status=status.HTTP_404_NOT_FOUND)
    except ObjectDoesNotExist:
      return Response({'message': 'No se encontró la observación con ese id.'}, status=status.HTTP_404_NOT_FOUND)


#===============================================================
# ObservationView para crear y listar observaciones
#===============================================================
class ObservationListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  parser_classes = [MultiPartParser, FormParser]
  
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
    request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'idProcessUserCeprunsaRelation': {'type': 'integer'},
                    'date': {'type': 'string', 'format': 'date'},
                    'lastEditDate': {'type': 'string', 'format': 'date'},
                    'observation': {'type': 'string'},
                    'document': {
                        'type': 'string',
                        'format': 'binary',  # Esto hace que Swagger muestre el selector de archivos
                        'description': 'Archivo adjunto'
                    },
                    'idRegisterBy': {'type': 'integer'},
                    'idLastEditedBy': {'type': 'integer'}
                }
            }
        },
    responses=ObservationSerializer
  )
  def post(self, request):
    serializer = ObservationSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
#===============================================================
# ObservationView para ver, actualizar y eliminar observaciones
#===============================================================
class ObservationDetailEditView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary='Ver una observación',
    description='Ver una observación por su ID.',
    responses=ObservationDetailSerializer
  )
  def get(self, request, pk):
    try:
      observation = Observation.objects.get(pk=pk)
    except ObjectDoesNotExist:
      return Response({'message': 'No se encontró la observación con ese id.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ObservationDetailSerializer(observation)
    return Response(serializer.data)
  
  @extend_schema(
    summary='Actualizar una observación',
    description='Actualizar una observación por su ID.',
    request=ObservationSerializer,
    responses=ObservationSerializer
  )
  def patch(self, request, pk):
    try:
      observation = Observation.objects.get(pk=pk)
    except ObjectDoesNotExist:
      return Response({'message': 'No se encontró la observación con ese id.'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ObservationSerializer(observation, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  @extend_schema(
    summary='Eliminar una observación',
    description='Eliminar una observación por su ID.',
    responses={200: None}
  )
  def delete(self, request, pk):
    try:
      observation = Observation.objects.get(pk=pk)
    except ObjectDoesNotExist:
      return Response({'message': 'No se encontró la observación con ese id.'}, status=status.HTTP_404_NOT_FOUND)
    
    observation.registerState = '*'
    observation.save()
    return Response(status=status.HTTP_204_NO_CONTENT)