from userAuth.models import UserCeprunsa
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from userAuth.serializers import UserCeprunsaSimpleSerializer, UserCeprunsaRolesAndInfosCreateSerializer, UserCeprunsaDetailSerializer, UserCeprunsaSimpleListSerializer
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.openapi import OpenApiParameter

#==============================================================================
#API para listar y crear usuarios
#==============================================================================
class UserCeprunsaSimpleListDetailedCreateView(APIView):
  permission_classes = [ IsAuthenticated ]
  
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
      userSerializer = self.get_user(request, userCeprunsa.id)
      return Response(userSerializer, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @extend_schema(
    summary="Listar usuarios Ceprunsa",
    description="Lista todos los usuarios Ceprunsa con algunos datos personales y roles",
    responses={200: UserCeprunsaSimpleListSerializer(many=True)},
    methods=['GET']
  )
  def get(self, request):
    users = UserCeprunsa.objects.select_related('userceprunsapersonalinfo').all()
    serializer = UserCeprunsaSimpleListSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#==============================================================================
#API para ver, editar y eliminar usuarios por id
#==============================================================================
class UserCeprunsaDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  
  serializer_class = UserCeprunsaRolesAndInfosCreateSerializer
  
  
  def get_object(self, pk):
    try:
      userCeprunsa = UserCeprunsa.objects.get(id=pk)
      return UserCeprunsaDetailSerializer(userCeprunsa).data
    except ObjectDoesNotExist:
      return None
  @extend_schema(
    summary="Ver usuario Ceprunsa por id",
    description="Muestra un usuario Ceprunsa con sus roles, datos personales e información de pago",
    responses={200: UserCeprunsaDetailSerializer},
    parameters=[
      #OpenApiParameter(name='pk', type=OpenApiTypes.INT, description='Id del usuario Ceprunsa')
    ]
  )  
  def get(self, request, pk):
    userCeprunsaSerialiser = self.get_object(pk)
    if not userCeprunsaSerialiser:
      return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    #serializer = UserCeprunsaSimpleSerializer(userCeprunsa)
    return Response(userCeprunsaSerialiser, status=status.HTTP_200_OK)


#==============================================================================
#API para devolver true si el usuario existe
#==============================================================================
class UserCeprunsaExistsView(APIView):
  #permission_classes = [IsAuthenticated]
  @extend_schema(
    summary="Verificar si el usuario Ceprunsa existe",
    description="Verifica si el usuario Ceprunsa existe por email",
    responses={200: {'exists': True}},
    #parameters=[OpenApiParameter(name='email', type=OpenApiTypes.STR, description='Email del usuario Ceprunsa')]
  )
  def get(self, request, email):
    try:
      #email = request.query_params.get('email')
      userCeprunsa = UserCeprunsa.objects.get(email=email)
      return Response({'exists': True}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
      return Response({'exists': False}, status=status.HTTP_200_OK)


#api para listar y crear usuarios
#class UserCeprunsaListCreateView(APIView):
#  permission_classes = [IsAuthenticated]
#  def get(self, request):
#    includeInactive = request.query_params.get('includeInactive', 'false').lower() == 'true'
#    
#    if includeInactive:
#      users = UserCeprunsa.objects.all()
#    else:
#      users = UserCeprunsa.objects.filter(registerState='A')
#    
#    serializer = UserCeprunsaSimpleSerializer(users, many=True)
#    return Response(serializer.data)
#  
#  def post(self, request):
#    serializer = UserCeprunsaSimpleSerializer(data=request.data)
#    if serializer.is_valid():
#      serializer.save()
#      return Response(serializer.data, status=status.HTTP_201_CREATED)
#    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#api para ver, editar y eliminar usuarios
#class UserCeprunsaDetailView(APIView):
#  permission_classes = [IsAuthenticated]
  
  #método para obtener un usuario por id reusable
#  def get_object(self, pk):
#    try:
#      return UserCeprunsa.objects.get(id=pk)
#    except ObjectDoesNotExist:
#      return None
  
  #obtención de un usuario por id
#  def get(self, request, pk):
#    userCeprunsa = self.get_object(pk)
#    if not userCeprunsa:
#      return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
#    serializer = UserCeprunsaSimpleSerializer(userCeprunsa)
#    return Response(serializer.data)
  
  #actualización de un usuario por id
#  def put(self, request, pk):
#    userCeprunsa = self.get_object(pk)
#    if not userCeprunsa:
#      return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
#    serializer = UserCeprunsaSimpleSerializer(userCeprunsa, data=request.data)
#    if serializer.is_valid():
#      serializer.save()
#      return Response(serializer.data)
#    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de un usuario por id
#  def delete(self, request, pk):
#    userCeprunsa = self.get_object(pk)
#    if not userCeprunsa:
#      return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
#    userCeprunsa.registerState = 'I'
#    userCeprunsa.save()
#    return Response({'message': 'Usuario eliminado'}, status=status.HTTP_204_NO_CONTENT)