from rest_framework_simplejwt.tokens import RefreshToken
from userAuth.models import UserCeprunsa
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from userAuth.models import UserCeprunsaRoleRelation
import requests
import datetime

from userAuth.serializers import RefreshTokenRequestSerializer

from drf_spectacular.utils import extend_schema

from rest_framework.permissions import IsAuthenticated

#===============================================================
#API para cerrar sesión
#===============================================================
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
      refreshToken = request.data['refresh']
      token = RefreshToken(refreshToken)
      token.blacklist()
      return Response(
        {'message': 'Logout exitoso'},
        status=status.HTTP_200_OK)
      
    except Exception as e:
      return Response(
        {'message': 'Error al cerrar sesión'},
        status=status.HTTP_400_BAD_REQUEST)

#===============================================================
#API para refrescar token
#===============================================================    
class RefreshTokenView(APIView):
  #No se comprobará si el usuario está autenticado, solo si el token de refresco es válido
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Refrescar token",
    description="Refresca el token de acceso",
    request=RefreshTokenRequestSerializer,
    responses={200: {
            "type": "object",
            "properties": {
                "access": {"type": "string", "description": "Nuevo token de acceso"},
                "access_expiration": {"type": "integer", "description": "Fecha de expiración del token en formato timestamp"},
                "refresh": {"type": "string", "description": "Nuevo token de refresco"}
            }
        }, 400: "Error al refrescar el token"},
    methods=['POST']
  )
  def post(self, request):
    try:
      refreshToken = request.data.get('refresh')
      
      if not refreshToken:
        return Response(
          {'message': 'No se proporcionó un token de refresco'},
          status=status.HTTP_400_BAD_REQUEST
          )
        
      oldRefreshToken = RefreshToken(refreshToken)
      newAccessToken = oldRefreshToken.access_token
      newRefreshToken = RefreshToken.for_user(request.user)
      
      accessExpiration = datetime.datetime.fromtimestamp(newAccessToken['exp'])
      
      return Response(
        {'access': str(newAccessToken),
         'access_expiration': accessExpiration,
         'refresh': str(newRefreshToken)},
        status=status.HTTP_200_OK
        )
      
    except Exception as e:
      return Response(
        {'message': 'Error al refrescar el token'},
        status=status.HTTP_400_BAD_REQUEST
        )

#===============================================================
#API para autenticación con Google
#===============================================================
class GoogleAuthView(APIView):
  @extend_schema(
    summary="Autenticación con Google",
    description="Autentica a un usuario con Google",
    responses={
      200: {"refresh": "str", "access": "str",
            "access_expiration": "datetime",
            "user":{
              "email": "str", "name": "str",
              "picture": "str", "id": "int"
            },
            "roles": [{"id": "int", "name": "str"}]},
      401: "Usuario no está registrado",
      400: "Token inválido"},
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
        accessToken = refresh.access_token
        
        # Obtén la expiración del token de acceso
        access_expiration = datetime.datetime.fromtimestamp(accessToken['exp'])
        
        # Información adicional del usuario
        user_data = {
          'email': user.email,
          'name': google_user['name'],
          'picture': google_user['picture'],
          'id': user.id
        }
        
        return Response({
          'refresh': str(refresh),
          'access': str(accessToken),
          'access_expiration': access_expiration,  # Fecha de expiración del token
          'user': user_data,
          'roles': roles
        })
      
      except ObjectDoesNotExist:
        return Response({'message': 'User no está registrado'}, status=401)
    
    return Response({'message': 'Token inválido'}, status=status.HTTP_400_BAD_REQUEST)
