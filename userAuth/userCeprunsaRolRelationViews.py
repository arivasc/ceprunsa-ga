from userAuth.models import UserCeprunsaRoleRelation, UserCeprunsa
from userAuth.serializers import UserCeprunsaRolRelationSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist



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