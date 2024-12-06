from userAuth.models import UserCeprunsaRoleRelation, UserCeprunsa, RoleCeprunsa
from userAuth.serializers import UserCeprunsaRolRelationSerializer, RoleCeprunsaSimpleSerializer, UserRoleAssignmentRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist

from django.db import transaction
from drf_spectacular.utils import extend_schema
from drf_spectacular.types import OpenApiTypes

#===============================================================
#API para manejar relaciones de usuario-rol
#===============================================================
class UserCerpunsaRoleRelacionManagementView(APIView):
  
  @extend_schema(
    summary="Asignar roles a usuario",
    description="Asigna roles a un usuario",
    request=UserRoleAssignmentRequestSerializer,
    responses={200: RoleCeprunsaSimpleSerializer(many=True), 400: {"description": "Debe asignar al menos un rol y como máximo dos"}},
    methods=['POST']
  )
  def post(self, request, pk):
    serializer = UserRoleAssignmentRequestSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    newRoles = serializer.validated_data['roles']
    currentRoles = UserCeprunsaRoleRelation.objects.filter(idUser=pk,)
    
    currentRolesIds = set(currentRoles.values_list('idRole', flat=True))
    newRolesIds = set(newRoles)
    
    rolesToAdd = newRolesIds - currentRolesIds
    
    rolesToRestore = newRolesIds & currentRolesIds
    
    rolesToRemove = currentRolesIds - newRolesIds
    #print(
    #  "newRolesIds", newRolesIds, "\nroles",newRoles,"\ncurrentRoles",currentRoles,
    #  "\ncurrentRolesIds", currentRolesIds,"\nrolesToRestore",rolesToRestore,
    #  "\nrolesToAdd", rolesToAdd, "\nrolesToRemove", rolesToRemove) #logs xd
    
    # Delete roles
    UserCeprunsaRoleRelation.objects.filter(idUser=pk, idRole__in=rolesToRemove).update(registerState='*')
    
    # Restore roles that were deleted
    UserCeprunsaRoleRelation.objects.filter(idUser=pk, idRole__in=rolesToRestore).update(registerState='A')
    
    currentRoles = currentRoles.filter(registerState='*')
    rolesToCreate = rolesToAdd.copy()
    
    # Update roles and activate them
    if currentRoles.exists():
      for role, roleId in zip(currentRoles, rolesToAdd):
        print("role", role, "roleId", roleId)
        role.idRole = RoleCeprunsa.objects.get(id=roleId)
        role.registerState = 'A'
        role.save()
        rolesToCreate.remove(roleId)
    
    # Create new roles
    if rolesToCreate:
      for roleId in rolesToCreate:
        UserCeprunsaRoleRelation.objects.update_or_create(idUser_id=pk, idRole_id=roleId)
    
    role_relations = UserCeprunsaRoleRelation.objects.filter(idUser=pk, registerState='A')
    roles = RoleCeprunsa.objects.filter(id__in=role_relations.values_list('idRole', flat=True))
    serializer = RoleCeprunsaSimpleSerializer(roles, many=True)
        
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    #return Response({'message': 'Error al asignar roles'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class UserCeprunsaRoleUpdateView(APIView):
  
  
  def get_object(self, pk):
    try:
      return UserCeprunsa.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
    
  def get(self, request, pk):
    user = self.get_object(pk)
    if not user:
      return Response({'message': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaRolRelationSerializer(user)
    return Response(serializer.data)







class UserCeprunsaRolRelationListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  def post(self, request):
    serializer = UserCeprunsaRolRelationSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
    if includeAll:
      userCeprunsaRolRelations = UserCeprunsaRoleRelation.objects.all()
    else:
      filter = request.query_params.get('filter', 'A').upper()
      userCeprunsaRolRelations = UserCeprunsaRoleRelation.objects.filter(registerState=filter)
    
    serializer = UserCeprunsaRolRelationSerializer(userCeprunsaRolRelations, many=True)
    return Response(serializer.data)
  
class UserCeprunsaRolRelationDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get_object_by_user(self, pk):
    try:
      return UserCeprunsaRoleRelation.objects.all(idUserCeprunsa=pk, registerState='A')
    except ObjectDoesNotExist:
      return None
  
  def get_object(self, pk):
    try:
      return UserCeprunsaRoleRelation.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  def get(self, request, pk):
    userCeprunsaRolesRelation = self.get_object_by_user(pk)
    if not userCeprunsaRolesRelation:
      return Response({'message': 'Relación usuario-rol no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaRolRelationSerializer(userCeprunsaRolesRelation, many=True)
    return Response(serializer.data)
  
  def put(self, request, pk):
    userCeprunsaRoleRelation = self.get_object(pk)
    if not userCeprunsaRoleRelation:
      return Response({'message': 'Relación usuario-rol no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaRolRelationSerializer(userCeprunsaRoleRelation, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def delete(self, request, pk):
    userCeprunsaRoleRelation = self.get_object(pk)
    if not userCeprunsaRoleRelation:
      return Response({'message': 'Relación usuario-rol no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    userCeprunsaRoleRelation.delete()
    return Response({'message': 'Relación usuario-rol eliminada'}, status=status.HTTP_204_NO_CONTENT)