from processes.models import Process
from processes.serializers import DetailedProcessSerializer, SimpleListProcessSerializer

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProcessListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
      
    if includeAll:
      processes = Process.objects.all()
    else:
      filter = request.query_params.get('filter', 'A').upper()        
      processes = Process.objects.filter(registerState=filter)
      
    serializer = SimpleListProcessSerializer(processes, many=True)
    return Response(serializer.data)
    
  def post(self, request):
    serializer = DetailedProcessSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProcessDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  #método para obtener un proceso por id reusable
  def get_object(self, pk):
    try:
      return Process.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de un proceso por id
  def get(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process)
    return Response(serializer.data)
  
  #actualización de un proceso por id
  def put(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de un proceso por id
  def delete(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    process.registerState = '*'
    process.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

