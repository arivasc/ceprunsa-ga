from django.urls import path
from userAuth.googleAuthViews import GoogleAuthView, RefreshTokenView, LogOutView
from userAuth.rolViews import RoleCeprunsaListCreateView, RoleCeprunsaDetailView
from userAuth.userCeprunsaViews import UserCeprunsaDetailView, UserCeprunsaSimpleListDetailedCreateView
from userAuth.userCeprunsaRolRelationViews import UserCeprunsaRolRelationListCreateView, UserCeprunsaRolRelationDetailView
#from userAuth.userCeprunsaCreateViews import UserCeprunsaCreateDetailView

urlpatterns = [
  path('google-auth', GoogleAuthView.as_view(), name='google-auth'),
  path('roles', RoleCeprunsaListCreateView.as_view(), name='roles'),
  path('roles/<int:pk>', RoleCeprunsaDetailView.as_view(), name='roles-detail'),
  
  #rutas para listar y crear usuarios
  path('users', UserCeprunsaSimpleListDetailedCreateView.as_view(), name='users'),
  path('users/<int:pk>', UserCeprunsaDetailView.as_view(), name='user-detail'),
  
  #nuevo endpoint para crear usuario con roles, personalInfo y payment
  #path('users/create', UserCeprunsaCreateDetailView.as_view(), name='user-create'),
  
  #endpoints para refrescar token y cerrar sesion
  path('users/refreshtoken', RefreshTokenView.as_view(), name='refresh-token'),
  path('users/logout', LogOutView.as_view(), name='logout'),
  
  
  path('user-rol-relations', UserCeprunsaRolRelationListCreateView.as_view(), name='user-rol-relations'),
  path('user-rol-relations/<int:pk>', UserCeprunsaRolRelationDetailView.as_view(), name='user-rol-relation-detail'),  
]