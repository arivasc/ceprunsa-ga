from processes.models import Process
from processes.serializers import DetailedProcessSerializer, SimpleListProcessSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema


#==============================================================================
#API para listar y crear procesos
#==============================================================================

class ProcessListCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Mostrar procesos",
    description="Muestra todos los procesos registrados.",
    responses={200: DetailedProcessSerializer(many=True)}
  )
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
      
    if includeAll:
      processes = Process.objects.all()
    else:
      #filter = request.query_params.get('filter', 'A').upper()        
      processes = Process.objects.exclude(registerState='*')
      
    serializer = SimpleListProcessSerializer(processes, many=True)
    return Response(serializer.data)
  
  @extend_schema(
    summary="Crear proceso",
    description="Crea un proceso con sus datos.",
    request=DetailedProcessSerializer,
    responses={201: DetailedProcessSerializer}
  )  
  def post(self, request):
    serializer = DetailedProcessSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#==============================================================================
#API para ver, editar y eliminar procesos por id
#==============================================================================

class ProcessDetailView(APIView):
  #permission_classes = [IsAuthenticated]
  
  #método para obtener un proceso por id reusable
  def get_object(self, pk):
    try:
      return Process.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de un proceso por id
  @extend_schema(
    summary="Ver proceso por id",
    description="Muestra un proceso con sus datos.",
    responses={200: DetailedProcessSerializer}
  )
  def get(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process)
    return Response(serializer.data)
  
  #actualización de un proceso por id
  @extend_schema(
    summary="Editar proceso por id",
    description="Edita un proceso con sus datos.",
    request=DetailedProcessSerializer,
    responses={200: DetailedProcessSerializer}
  )
  def put(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de un proceso por id
  @extend_schema(
    summary="Eliminar proceso por id",
    description="Elimina un proceso.",
    responses={204: 'No Content'}
  )
  def delete(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    process.registerState = '*'
    process.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

