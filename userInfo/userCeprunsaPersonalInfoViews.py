from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from userInfo.models import UserCeprunsaPersonalInfo
from userInfo.serializers import UserCeprunsaPersonalInfoSerializer
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

class UserCeprunsaPersonalInfoListCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    
    userCeprunsaPersonalInfo = UserCeprunsaPersonalInfo.objects.all()
    serializer = UserCeprunsaPersonalInfoSerializer(userCeprunsaPersonalInfo, many=True)
    return Response(serializer.data)
  
  def post(self, request):
    serializer = UserCeprunsaPersonalInfoSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCeprunsaPersonalInfoDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get_object_by_user(self, pk):
    try:
      return UserCeprunsaPersonalInfo.objects.get(idUserCeprunsa=pk)
    except ObjectDoesNotExist:
      return None

  def get(self, request, pk):
    userCeprunsaPersonalInfo = self.get_object_by_user(pk)
    if not userCeprunsaPersonalInfo:
      return Response({'message': 'Información personal de el usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaPersonalInfoSerializer(userCeprunsaPersonalInfo)
    return Response(serializer.data)
  
  def put(self, request, pk):
    userCeprunsaPersonalInfo = self.get_object_by_user(pk)
    if not userCeprunsaPersonalInfo:
      return Response({'message': 'Información personal de el usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaPersonalInfoSerializer(userCeprunsaPersonalInfo, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def delete(self, request, pk):
    userCeprunsaPersonalInfo = self.get_object_by_user(pk)
    if not userCeprunsaPersonalInfo:
      return Response({'message': 'Información personal de el usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    userCeprunsaPersonalInfo.delete()
    return Response({'message': 'Información personal de el usuario eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)