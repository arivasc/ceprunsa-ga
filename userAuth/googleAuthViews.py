from rest_framework_simplejwt.tokens import RefreshToken
from userAuth.models import UserCeprunsa
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from userAuth.models import UserCeprunsaRoleRelation
import requests
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.permissions import IsAuthenticated

class LogOutView(APIView):
  permission_classes = [IsAuthenticated]
  
  
  @swagger_auto_schema(
    operation_description="Cerrar sesion, se añade el refresh token a la blacklist",
    responses={200: "OK", 400: "Error en la solicitud"},
  )
  def post(self, request):
    try:
      refresh_token = request.data['refresh']
      token = RefreshToken(refresh_token)
      token.blacklist()
      return Response({'message': 'Logout exitoso'}, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'message': 'Error al cerrar sesión'}, status=status.HTTP_400_BAD_REQUEST)
    
class RefreshTokenView(APIView):
  permission_classes = [IsAuthenticated]
  @swagger_auto_schema(
    operation_description="Refrescar el token de acceso",
    responses={200: "OK", 400: "Error en la solicitud"},
  )
  def post(self, request):
    try:
      refresh_token = request.data['refresh']
      token = RefreshToken(refresh_token)
      access_token = str(token.access_token)
      return Response({'access': access_token})
    except Exception as e:
      return Response({'message': 'Error al refrescar el token'}, status=status.HTTP_400_BAD_REQUEST)



class GoogleAuthView(APIView):
  @swagger_auto_schema(
    operation_description="Autenticación con Google",
    request_body=openapi.Schema(
      type=openapi.TYPE_OBJECT,
      properties={
        'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de Google'),
      }
    ),
    responses={200: "OK", 400: "Error en la solicitud"},
  )
  def post(self, request):
    tokenId = request.data.get('token')
    response = requests.get(f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={tokenId}')
    
    if response.status_code == 200:
      google_user = response.json()
      email = google_user['email']
      try:
        user = UserCeprunsa.objects.get(email=email)
        
        roles = UserCeprunsaRoleRelation.objects.filter(idUser=user).values('idRole__name')
        
        # Genera los tokens de acceso y refresco
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        # Obtén la expiración del token de acceso
        access_expiration = datetime.datetime.fromtimestamp(access_token['exp'])
        
        # Información adicional del usuario
        user_data = {
          'email': user.email,
          'name': google_user['name'],
          'picture': google_user['picture'],  # Asegúrate de que el campo 'name' existe en el modelo UserCeprunsa
          'id': user.id
        }
        
        return Response({
          'refresh': str(refresh),
          'access': str(access_token),
          'access_expiration': access_expiration,  # Fecha de expiración del token
          'user': user_data,
          'roles': roles
        })
      
      except ObjectDoesNotExist:
        return Response({'message': 'User no está registrado'}, status=401)
    
    return Response({'message': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
