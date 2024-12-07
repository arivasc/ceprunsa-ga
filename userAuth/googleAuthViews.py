from rest_framework_simplejwt.tokens import RefreshToken
from userAuth.models import UserCeprunsa
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from userAuth.models import UserCeprunsaRoleRelation
import requests
import datetime
from drf_spectacular.utils import extend_schema

from rest_framework.permissions import IsAuthenticated

class LogOutView(APIView):
  permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Cerrar sesión",
    description="Cierra la sesión del usuario",
    responses={200: "OK", 400: "Error en la solicitud"},
    #request=OpenApiTypes.STR,
    methods=['POST']
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
  
  @extend_schema(
    summary="Refrescar token",
    description="Refresca el token de acceso",
    responses={200: {"access": "str"}, 400: "Error al refrescar el token"},
    methods=['POST']
  )
  def post(self, request):
    try:
      refresh_token = request.data['refresh']
      token = RefreshToken(refresh_token)
      access_token = str(token.access_token)
      access_expiration = datetime.datetime.fromtimestamp(access_token['exp'])
      return Response({'access': access_token, 'access_expiration':access_expiration, 'refres':token}, status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'message': 'Error al refrescar el token'}, status=status.HTTP_400_BAD_REQUEST)



class GoogleAuthView(APIView):
  @extend_schema(
    summary="Autenticación con Google",
    description="Autentica a un usuario con Google",
    responses={200: {"refresh": "str", "access": "str", "access_expiration": "datetime", "user": {"email": "str", "name": "str", "picture": "str", "id": "int"}, "roles": [{"id": "int", "name": "str"}]}, 401: "Usuario no está registrado", 400: "Token inválido"},
    methods=['POST']
  )
  def post(self, request):
    tokenId = request.data.get('token')
    response = requests.get(f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={tokenId}')
    
    if response.status_code == 200:
      google_user = response.json()
      email = google_user['email']
      try:
        user = UserCeprunsa.objects.get(email=email, registerState='A')
        
        roles = UserCeprunsaRoleRelation.objects.filter(idUser=user, registerState='A').values('idRole__name')
        
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
