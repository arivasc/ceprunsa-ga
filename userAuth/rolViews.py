from rest_framework.views import APIView
from rest_framework.response import Response

#parte de administración de grupos
from userAuth.models import RoleCeprunsa
from userAuth.serializers import RoleCeprunsaSerializer

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

#api para listar y crear roles
class RoleCeprunsaListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  def get(self, request):
    includeInactive = request.query_params.get('includeInactive', 'false').lower() == 'true'
    
    if includeInactive:
      roles = RoleCeprunsa.objects.all()
    else:
      roles = RoleCeprunsa.objects.filter(registerState='A')
    
    serializer = RoleCeprunsaSerializer(roles, many=True)
    return Response(serializer.data)
  
  def post(self, request):
    serializer = RoleCeprunsaSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#api para ver, editar y eliminar roles
class RoleCeprunsaDetailView(APIView):
  #permission_classes = [IsAuthenticated]
  
  #método para obtener un rol por id reusable
  def get_object(self, pk):
    try:
      return RoleCeprunsa.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de un rol por id
  def get(self, request, pk):
    rolCeprunsa = self.get_object(pk)
    if not rolCeprunsa:
      return Response({'message': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = RoleCeprunsaSerializer(rolCeprunsa)
    return Response(serializer.data)
  
  #actualización de un rol por id
  def put(self, request, pk):
    rolCeprunsa = self.get_object(pk)
    if not rolCeprunsa:
      return Response({'message': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = RoleCeprunsaSerializer(rolCeprunsa, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de un rol por id
  def delete(self, request, pk):
    rolCeprunsa = self.get_object(pk)
    if not rolCeprunsa:
      return Response({'message': 'Rol no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    rolCeprunsa.registerState = 'I'
    rolCeprunsa.save()
    return Response({'message': 'Rol eliminado'}, status=status.HTTP_204_NO_CONTENT)