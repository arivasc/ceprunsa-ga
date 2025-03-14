from userAuth.models import UserCeprunsa
from courses.models import Course
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from userAuth.serializers import UserCeprunsaRolesAndInfosCreateSerializer, UserCeprunsaDetailSerializer, UserCeprunsaSimpleListSerializer, UserCeprunsaToEditSerializer
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.openapi import OpenApiParameter

#==============================================================================
#API para listar y crear usuarios
#==============================================================================
class UserCeprunsaSimpleListDetailedCreateView(APIView):
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
      userSerializer = self.get_user(request, userCeprunsa.id)
      return Response(userSerializer, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @extend_schema(
    summary="Listar usuarios Ceprunsa con opción de filtro por rol",
    description=(
      "Devuelve una lista de usuarios Ceprunsa con datos básicos, "
      "y permite filtrar por un rol específico si se proporciona el ID del rol en el cuerpo de la solicitud. "
      "Si no se especifica un rol, se devuelven todos los usuarios activos. "
      "Los usuarios con estado de registro inactivo ('*') siempre se excluyen."
    ),
    request={
      "application/json": {
        'type': 'object',
        'properties': {
          'role': {
            'type': 'string',
            'description': "ID del rol por el cual filtrar los usuarios (opcional)."
          },
        },
        'required': ["role"],
        "example": {"role": "1"},
      }
    },
    responses={
      200: OpenApiExample(
        "Usuarios listados exitosamente",
        value={
          "results": [
          {
              "id": 1,
              "username": "jdoe",
              "email": "jdoe@example.com",
              "firstName": "John",
              "lastName": "Doe",
              "roles": [
                  {"id": 2, "name": "Docente"},
                  {"id": 3, "name": "Supervisor"}
              ],
            },
            {
              "id": 2,
              "username": "asmith",
              "email": "asmith@example.com",
              "firstName": "Anna",
              "lastName": "Smith",
              "roles": [{"id": 4, "name": "Coordinador"}],
            },
          ]
        },
      ),
      400: OpenApiExample(
        "Solicitud inválida",
        value={
          "detail": "El ID del rol debe ser un número entero válido.",
        },
      ),
    },
    examples=[
      OpenApiExample(
          "Ejemplo de solicitud con filtro por rol",
          value={"role": 2},
          request_only=True,
      ),
      OpenApiExample(
        "Ejemplo de respuesta sin filtro",
        value={
          "results": [
            {
              "id": 1,
              "username": "jdoe",
              "email": "jdoe@example.com",
              "firstName": "John",
              "lastName": "Doe",
              "roles": [
                {"id": 2, "name": "Docente"},
                {"id": 3, "name": "Supervisor"}
              ],
            }
          ]
        },
        response_only=True,
      ),
    ],
  )
  def get(self, request):
    roleId = request.query_params.get('role', None)
    search = request.query_params.get('search', None)
    process = request.query_params.get('process', None)
    notRelated = request.query_params.get('notRelated', None)
    if not roleId:
      users = UserCeprunsa.objects.select_related(
        'userceprunsapersonalinfo').all().exclude(registerState='*').order_by('id')
      
    else:
      users = UserCeprunsa.objects.select_related(
        'userceprunsapersonalinfo').filter(
        userceprunsarolerelation__idRole=roleId,
        userceprunsarolerelation__registerState='A').all().exclude(registerState='*').order_by('id')
        
    if notRelated:
      if roleId == 4:
        coordIds = Course.objects.filter(coordinator__isnull=False).values_list('coordinator', flat=True)
      elif roleId == 5:
        coordIds = Course.objects.filter(subCoordinator__isnull=False).values_list('subCoordinator', flat=True)
      elif roleId == 6:
        users = users.filter
        coordIds = Course.objects.filter(courseteacherrelation__isnull=False).values_list('courseteacherrelation__teacher', flat=True)
      
      users = users.exclude(id__in=coordIds)
    
    if search:
      users = users.filter(userceprunsapersonalinfo__names__icontains=search) | users.filter(userceprunsapersonalinfo__lastNames__icontains=search)
    pagination = PageNumberPagination()
    pagination.page_size = 30
    
    paginatedUsers = pagination.paginate_queryset(users, request)
    
    serializer = UserCeprunsaSimpleListSerializer(paginatedUsers, many=True)
    
    
    return pagination.get_paginated_response(serializer.data)


#==============================================================================
#API para ver, editar y eliminar usuarios por id
#==============================================================================
class UserCeprunsaDetailView(APIView):
  permission_classes = [IsAuthenticated]
   
  def get_object(self, pk):
    try:
      userCeprunsa = UserCeprunsa.objects.get(id=pk)
      return UserCeprunsaDetailSerializer(userCeprunsa).data
    except ObjectDoesNotExist:
      return None
    
  @extend_schema(
    summary="Ver usuario Ceprunsa por id",
    description="Muestra un usuario Ceprunsa con sus roles, datos personales e información de pago",
    responses={200: UserCeprunsaDetailSerializer, 404: 'Usuario no encontrado'},
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
  
  def update(self, request, pk):
    userCeprunsa = UserCeprunsa.objects.get(id=pk)
    if not userCeprunsa:
      return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaToEditSerializer(userCeprunsa, data=request.data)
    if serializer.is_valid():
      serializer.save()
      serializerReturn = UserCeprunsaDetailSerializer(serializer.instance)
      return Response(serializerReturn.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  @extend_schema(
    summary="Actualización completa de usuario Ceprunsa por id",
    description="Edita un usuario Ceprunsa con sus datos personales e información de pago",
    request=UserCeprunsaToEditSerializer,
    responses={
      200: UserCeprunsaDetailSerializer,
      400: "Error al actualizar el usuario",
      404: "Usuario no encontrado"}
  )
  def put(self, request, pk):
    return self.update(request, pk)
  
  @extend_schema(
    summary="Actualización parcial de usuario Ceprunsa por id",
    description="Edita un usuario Ceprunsa con sus datos personales e información de pago",
    request=UserCeprunsaToEditSerializer,
    responses={
      200: UserCeprunsaDetailSerializer,
      400: "Error al actualizar el usuario",
      404: "Usuario no encontrado"}
  )
  def patch(self, request, pk):
    return self.update(request, pk)
  
  
  
  
  @extend_schema(
    summary="Eliminar usuario Ceprunsa por id",
    description="Elimina un usuario Ceprunsa",
    responses={204: 'Usuario eliminado', 404: 'Usuario no encontrado'},
  )
  def delete(self, request, pk):
    try:
        userCeprunsa = UserCeprunsa.objects.get(id=pk)

        if userCeprunsa.registerState == '*':
            return Response({'message': 'Usuario ya está eliminado'}, status=status.HTTP_400_BAD_REQUEST)
        
    except UserCeprunsa.DoesNotExist:
        return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    userCeprunsa.registerState = '*'
    userCeprunsa.save()
    return Response({'message': 'Usuario eliminado'}, status=status.HTTP_204_NO_CONTENT)


#==============================================================================
#API para devolver true si el usuario existe
#==============================================================================
class UserCeprunsaExistsView(APIView):
  permission_classes = [IsAuthenticated]
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
      if userCeprunsa.registerState == '*':
        return Response({'exists': True, 'mensaje':'El usuario existe pero ha sido deshabilitado'}, status=status.HTTP_200_OK)
      return Response({'exists': True}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
      return Response({'exists': False}, status=status.HTTP_200_OK)

