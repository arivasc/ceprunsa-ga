from userInfo.serializers import UserCeprunsaPaymentInfoSerializer
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from userInfo.models import UserCeprunsaPaymentInfo
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserCeprunsaPaymentInfoListCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    includeInactive = request.query_params.get('includeInactive', 'false').lower() == 'true'
    
    if includeInactive:
      users = UserCeprunsaPaymentInfo.objects.all()
    else:
      users = UserCeprunsaPaymentInfo.objects.filter(registerState='A')
    
    serializer = UserCeprunsaPaymentInfoSerializer(users, many=True)
    return Response(serializer.data)
  
  def post(self, request):
    serializer = UserCeprunsaPaymentInfoSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserCeprunsaPaymentInfoDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  #método para obtener información de pago por id reusable
  def get_object(self, pk):
    try:
      return UserCeprunsaPaymentInfo.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de información de pago por id de usuario
  def get_object_by_user(self, pk):
    try:
      return UserCeprunsaPaymentInfo.objects.get(idUserCeprunsa=pk)
    except ObjectDoesNotExist:
      return None
  
  #método get para obtener información de pago por id de usuario
  def get(self, request, pk):
    userCeprunsaPaymentInfo = self.get_object_by_user(pk)
    if not userCeprunsaPaymentInfo:
      return Response({'message': 'Información de pago de el usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaPaymentInfoSerializer(userCeprunsaPaymentInfo)
    return Response(serializer.data)
  
  #metodo put para actualizar información de pago por id de usuario
  def put(self, request, pk):
    userCeprunsaPaymentInfo = self.get_object_by_user(pk)
    if not userCeprunsaPaymentInfo:
      return Response({'message': 'Información de pago de el usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserCeprunsaPaymentInfoSerializer(userCeprunsaPaymentInfo, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #metodo delete para eliminar información de pago por id de usuario
  def delete(self, request, pk):
    userCeprunsaPaymentInfo = self.get_object_by_user(pk)
    if not userCeprunsaPaymentInfo:
      return Response({'message': 'Información de pago de el usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    userCeprunsaPaymentInfo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)