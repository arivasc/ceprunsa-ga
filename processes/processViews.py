from processes.models import Process, ProcessUserCerprunsaRelation
from userAuth.models import UserCeprunsa, UserCeprunsaRoleRelation
from courses.models import CourseTeacherRelation, Course
from processes.serializers import (
  DetailedProcessSerializer,
  SimpleListProcessSerializer,
  ProcessUserCerprunsaRelationsListSerializer,
  ProcessUserCerprunsaRelationSerializer,
  ProcessUserCerprunsaRelationDetailSerializer)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

#==============================================================================
#API para cambiar el estado de un proceso
#==============================================================================
class ProcessStateChangeView(APIView):
  #permission_classes = [IsAuthenticated]
  @extend_schema(
    summary="Cambiar estado de un proceso",
    description="Cambia el estado de un proceso a uno nuevo especificado.",
    request={
      "application/json": {
        "type": "object",
        "properties": {
          "newState": {
            "type": "string",
            "description": "Nuevo estado del proceso.",
          },
        },
        "required": ["newState"],
        "example": {"newState": "C"},
      }
    },
    responses={200: {"message": "Estado del proceso modificado"},
               404: {"message": "Proceso no encontrado"},
               400: {"message": "Debe especificar un nuevo estado"}}
  )
  def post(self, request, pk):
    
    process = Process.objects.get(id=pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    newState = request.data.get('newState', 'Z').upper()
    if newState == 'Z':
      return Response({'message': 'Debe especificar un nuevo estado'},
                      status=status.HTTP_400_BAD_REQUEST
      )
    else:
      process.registerState = newState
      process.save()
      return Response({'message': 'Estado del proceso modificado'}, status=status.HTTP_200_OK)


#==============================================================================
#API para listar y crear relaciones entre usuarios y procesos
#==============================================================================
class ProcessUserCeprunsaRelationListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Mostrar relaciones usuarios-proceso",
    description="Muestra todas las relaciones entre usuarios y un proceso. Para incluir relaciones eliminadas, se debe especificar '?includeAll=true'.",
    responses={200: ProcessUserCerprunsaRelationsListSerializer(many=True)}
  )
  def get(self, request, pk):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
    
    if includeAll:
      relations = ProcessUserCerprunsaRelation.objects.filter(idProcess=pk)
    else:
      relations = ProcessUserCerprunsaRelation.objects.filter(idProcess=pk).exclude(registerState='*')
    
    serializer = ProcessUserCerprunsaRelationsListSerializer(relations, many=True)
    return Response(serializer.data)
  
  @extend_schema(
    summary="Asignar usuarios a un proceso",
    description=(
        "Asigna uno o más usuarios a un proceso especificado por su ID (pk). "
        "El usuario debe tener roles activos asignados, y la relación no debe existir previamente. "
        "Además, se puede proporcionar un nivel de calidad opcional para la relación. "
        "Los usuarios sin roles activos o relaciones ya existentes generan errores."
    ),
    request={
      "application/json": {
        "type": "object",
        "properties": {
          "users": {
              "type": "array",
              "items": {"type": "integer"},
              "description": "Lista de IDs de usuarios a asignar al proceso.",
          },
          "quality": {
              "type": "string",
              "description": "Nivel de calidad opcional para la relación.",
              "nullable": True,
          },
        },
        "required": ["users"],
        "example": {"users": [1, 2, 3], "quality": "2"},
      }
    },
    responses={
        201: OpenApiExample(
            "Asignaciones exitosas",
            value={
                "created": [
                    {
                        "id": 1,
                        "idUserCeprunsa": 5,
                        "idProcess": 10,
                        "idRole": 2,
                        "idCourse": None,
                        "startDate": "2024-01-01",
                        "endDate": "2024-12-31",
                        "quality": "Alta",
                    }
                ],
                "errors": [],
            },
        ),
        400: OpenApiExample(
            "Errores en las asignaciones",
            value={
                "created": [],
                "errors": [
                    "El usuario con id 3 no tiene roles asignados",
                    "El usuario con id 5 ya tiene una relación con el proceso CEPRUNSA y el rol Docente",
                ],
            },
        ),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de solicitud",
            value={
                "users": [5, 10, 15],
                "quality": "Alta",
            },
            request_only=True,
        ),
    ],
  )
  def post(self, request, pk):
    process = Process.objects.get(id=pk)
    relations = request.data.get('relations', [])
    
    if not isinstance(relations, list) or not relations:
      return Response({'message': 'Debe asignar al menos un usuario'}, status=status.HTTP_400_BAD_REQUEST)
    
    createdRelations = []
    errors = []
    
    for relation in relations:
      if not isinstance(relation, dict) or 'userId' not in relation:
        errors.append('Cada relación debe tener un campo "userId"')
        continue
      
      userId = relation['userId']
      quality = relation.get('quality', 'A')
      try:
        user = UserCeprunsa.objects.get(id=userId, registerState='A')
        print(user.email)
        hasRoles = UserCeprunsaRoleRelation.objects.filter(idUser=user, registerState='A')
        
        
        if not hasRoles:
          errors.append(f'El usuario con id {userId} no tiene roles asignados')
          continue
        
        for role in hasRoles:
          relation = ProcessUserCerprunsaRelation.objects.filter(idUserCeprunsa=user, idProcess=process, idRole=role.idRole)
          
          if relation:
            errors.append(f'El usuario con id {userId} ya tiene una relación con el proceso {process.name} y el rol {role.idRole.name}')
            continue
          
          course = None
          if role.idRole.name == 'Servidor de Enseñanza':
            courseRelation = CourseTeacherRelation.objects.filter(teacher=user)
            
            if not courseRelation:
              errors.append(f'El usuario con id {userId} y rol {role.idRole.name} no tiene un curso asignado')
              continue
            
            else:
              idCourse = CourseTeacherRelation.objects.get(teacher=user).course
              course = Course.objects.get(id=idCourse.id)
          
          elif role.idRole.name == 'Coordinador' or role.idRole.name == 'Sub-coordinador':
            course = Course.objects.filter(coordinator=user) or Course.objects.filter(subCoordinator=user)
            if not course:
              errors.append(f'El usuario con id {userId} y rol {role.idRole.name} no tiene un curso asignado')
              continue
          
          
          
          relation = ProcessUserCerprunsaRelation.objects.create(
            idUserCeprunsa=user,
            idProcess=process,
            idRole=role.idRole,
            idCourse= course,
            startDate = process.dateStart,
            endDate = process.dateEnd,
            quality=quality
          )
          createdRelations.append(relation)
            
      except ObjectDoesNotExist:
        errors.append(f'El usuario con id {userId} no existe')
    serializer = ProcessUserCerprunsaRelationSerializer(createdRelations, many=True)
    return Response(
      {'created': serializer.data,
       'errors': errors},
      status=status.HTTP_201_CREATED if createdRelations else status.HTTP_400_BAD_REQUEST)

#==============================================================================
#API para ver, editar y eliminar relaciones entre usuarios y procesos por id
#==============================================================================
class ProcessUserCeprunsaRelationDetailView(APIView):
  #permission_classes = [IsAuthenticated]
  
  #método para obtener una relación por id reusable
  def get_object(self, pk):
    try:
      return ProcessUserCerprunsaRelation.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de una relación por id
  @extend_schema(
    summary="Ver relación por id",
    description="Muestra una relación entre usuario y proceso con sus datos.",
    responses={200: ProcessUserCerprunsaRelationDetailSerializer}
  )
  def get(self, request, pk):
    relation = self.get_object(pk)
    if not relation:
      return Response({'message': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProcessUserCerprunsaRelationDetailSerializer(relation)
    return Response(serializer.data)
  
  #actualización de una relación por id
  @extend_schema(
    summary="Editar relación por id",
    description="Edita una relación entre usuario y proceso con sus datos.",
    request=ProcessUserCerprunsaRelationSerializer,
    responses={200: ProcessUserCerprunsaRelationSerializer}
  )
  def put(self, request, pk):
    relation = self.get_object(pk)
    if not relation:
      return Response({'message': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProcessUserCerprunsaRelationSerializer(relation, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de una relación por id
  @extend_schema(
    summary="Eliminar relación por id",
    description="Elimina una relación entre usuario y proceso.",
    responses={204: 'No Content'}
  )
  def delete(self, request, pk):
    relation = self.get_object(pk)
    if not relation:
      return Response({'message': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    relation.registerState = '*'
    relation.save()
    return Response(status=status.HTTP_204_NO_CONTENT)



#==============================================================================
#API para listar y crear procesos
#==============================================================================

class ProcessListCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Mostrar procesos",
    description="Muestra todos los procesos registrados.",
    responses={200: DetailedProcessSerializer(many=True)}
  )
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
      
    if includeAll:
      processes = Process.objects.all()
    else:
      #filter = request.query_params.get('filter', 'A').upper()        
      processes = Process.objects.exclude(registerState='*')
      
    serializer = SimpleListProcessSerializer(processes, many=True)
    return Response(serializer.data)
  
  @extend_schema(
    summary="Crear proceso",
    description="Crea un proceso con sus datos.",
    request=DetailedProcessSerializer,
    responses={201: DetailedProcessSerializer}
  )  
  def post(self, request):
    serializer = DetailedProcessSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#==============================================================================
#API para ver, editar y eliminar procesos por id
#==============================================================================

class ProcessDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  #método para obtener un proceso por id reusable
  def get_object(self, pk):
    try:
      return Process.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de un proceso por id
  @extend_schema(
    summary="Ver proceso por id",
    description="Muestra un proceso con sus datos.",
    responses={200: DetailedProcessSerializer}
  )
  def get(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process)
    return Response(serializer.data)
  
  #actualización de un proceso por id
  @extend_schema(
    summary="Editar proceso por id",
    description="Edita un proceso con sus datos.",
    request=DetailedProcessSerializer,
    responses={200: DetailedProcessSerializer}
  )
  def put(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de un proceso por id
  @extend_schema(
    summary="Eliminar proceso por id",
    description="Elimina un proceso.",
    responses={204: 'No Content'}
  )
  def delete(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    process.registerState = '*'
    process.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

