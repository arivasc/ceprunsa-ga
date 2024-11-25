from userAuth.serializers import UserCeprunsaRolesAndInfosCreateSerializer, UserCeprunsaResumeSerializer, UserCeprunsaDetailSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from userAuth.models import UserCeprunsa
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.utils import extend_schema

class UserCeprunsaCreateDetailView(APIView):
  #permission_classes = [ IsAuthenticated ]
  
  serializer_class = UserCeprunsaRolesAndInfosCreateSerializer
  
  
  def get_user(self, request, pk):
    #try:
        user = UserCeprunsa.objects.get(pk=pk)
        serializer = UserCeprunsaDetailSerializer(user)
        return serializer.data
        #return Response(serializer.data, status=status.HTTP_200_OK)
    #except UserCeprunsa.DoesNotExist:
        #return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
  @extend_schema(
    summary="Crear usuario Ceprunsa",
    description="Crea un usuario Ceprunsa con sus roles, datos personales e información de pago",
    request=UserCeprunsaRolesAndInfosCreateSerializer,
    responses={201: UserCeprunsaDetailSerializer}
  )  
  def post(self, request):
    serializer = self.serializer_class(data=request.data)
    if serializer.is_valid():
      userCeprunsa = serializer.save()
      print(userCeprunsa)
      userSerializer = self.get_user(request, userCeprunsa.id)
      return Response(userSerializer, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  
  
