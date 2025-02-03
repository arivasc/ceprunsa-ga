from courses.models import Course, CourseTeacherRelation
from userAuth.models import UserCeprunsa, UserCeprunsaRoleRelation
from courses.serializers import DetailedCourseSerializer, CourseSerializer, CourseTeacherRelationSerializer, DetailedCourseTeacherRelationSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

#==============================================================================
#API para listar y crear relaciones entre cursos y profesores
#==============================================================================
class CourseTeacherRelationCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
        summary="Asignar docentes a un curso",
        description=(
            "Permite asignar una lista de usuarios con el rol 'Servidor de enseñanza' a un curso específico, "
            "identificado por su `pk`. Verifica que cada usuario tenga el rol adecuado antes de asignarlo."
        ),
        
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "teachers": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Lista de IDs de usuarios a asignar al curso.",
                    }
                },
                "required": ["teachers"],
                "example": {"teachers": [1, 2, 3]},
            }
        },
        responses={
            201: {
                "description": "Relaciones creadas exitosamente.",
                "content": {
                    "application/json": {
                        "example": {
                            "created_relations": [
                                {"course": 1, "teacher": 1},
                                {"course": 1, "teacher": 2},
                            ],
                            "errors": [],
                        }
                    }
                },
            },
            400: {
                "description": "Error en la validación o asignación.",
                "content": {
                    "application/json": {
                        "example": {
                            "created_relations": [],
                            "errors": [
                                "Usuario con ID 3 no tiene el rol 'Servidor de enseñanza'.",
                                "Usuario 2 ya está asignado al curso.",
                            ],
                        }
                    }
                },
            },
            404: {
                "description": "Curso no encontrado.",
                "content": {
                    "application/json": {"example": {"detail": "No encontrado."}},
                },
            },
        },
    )
  def post(self, request, pk):
    course = get_object_or_404(Course, pk=pk)
    
    userIds = request.data.get('teachers', [])
    if not isinstance(userIds, list) or not userIds:
      return Response({'message': 'Debe enviar una lista de profesores'}, status=status.HTTP_400_BAD_REQUEST)
    
    createdRelations = []
    errors = []
    
    for userId in userIds:
      try:
        teacher = UserCeprunsa.objects.get(id=userId)
        hasRole = UserCeprunsaRoleRelation.objects.filter(idUser=userId, idRole=6).exists()
        if not hasRole:
          errors.append(f'El profesor con id {userId} no tiene el rol de profesor')
          continue
        relation, created = CourseTeacherRelation.objects.get_or_create(course=course, teacher=teacher)
        
        if created:
          createdRelations.append(relation)
        else:
          errors.append(f'El profesor con id {userId} ya tiene una relación con el curso')
        
      except ObjectDoesNotExist:
        errors.append(f'El profesor con id {userId} no existe')
    serializer = CourseTeacherRelationSerializer(createdRelations, many=True)
    return Response(
      {'created': serializer.data,
       'errors': errors},
      status=status.HTTP_201_CREATED if createdRelations else status.HTTP_400_BAD_REQUEST)
  
  @extend_schema(
    summary="Listar relaciones entre cursos y profesores",
    description="Lista todas las relaciones entre cursos y profesores",
    responses={200: CourseTeacherRelationSerializer(many=True)}
  )
  def get(self, request, pk):
    relations = CourseTeacherRelation.objects.filter(course=pk)
    serializer = DetailedCourseTeacherRelationSerializer(relations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
  @extend_schema(
    summary="Eliminar la relación entre un curso y un profesor",
    description="Elimina la relación entre un curso y un profesor",
    responses={204: 'Relacion eliminada'}
  )
  def delete(self, request, pk):
    relations = CourseTeacherRelation.objects.filter(id=pk)
    relations.delete()
    return Response({'message': 'Relacion eliminada'}, status=status.HTTP_204_NO_CONTENT)


#==============================================================================
#API para listar y crear cursos
#==============================================================================

class CourseCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Crear curso",
    description="Crea un curso con sus datos",
    request=CourseSerializer,
    responses={201: CourseSerializer,
               400: "Error al crear el curso",
               400: "El usuario no tiene el rol de coordinador",
               400: "El usuario no tiene el rol de sub-coordinador"}
  )
  def post(self, request):
    coordinator = request.data.get('coordinator')
    if coordinator:
      rol = UserCeprunsaRoleRelation.objects.filter(idUser=coordinator, idRole=4, registerState='A').exists()
      if not rol:
        return Response({'message': f'El usuario con id {coordinator} no tiene el rol de coordinador'},
                        status=status.HTTP_400_BAD_REQUEST)
    subCoordinator = request.data.get('subCoordinator')
    if subCoordinator:
      rol = UserCeprunsaRoleRelation.objects.filter(idUser=subCoordinator, idRole=5, registerState='A').exists()
      if not rol:
        return Response({'message': f'El usuario con id {subCoordinator} no tiene el rol de sub-coordinador'},
                        status=status.HTTP_400_BAD_REQUEST)
        
    serializer = CourseSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  @extend_schema(
    summary="Listar cursos",
    description="Lista todos los cursos registrados",
    responses={200: DetailedCourseSerializer(many=True)}
  )
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
    if includeAll:
      courses = Course.objects.all()
    else:
      filter = request.query_params.get('filter', 'A').upper()
      courses = Course.objects.select_related('coordinator__userceprunsapersonalinfo').filter(registerState=filter)
    
    serializer = DetailedCourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


#==============================================================================
#API para ver, editar y eliminar cursos por id
#==============================================================================

class CourseDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get_object(self, pk):
    try:
      return Course.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  @extend_schema(
    summary="Ver curso por id",
    description="Muestra un curso por su id",
    responses={200: DetailedCourseSerializer,
               404: 'Curso no encontrado'},
  )
  def get(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedCourseSerializer(course)
    return Response(serializer.data)
  
  @extend_schema(
    summary="Editar curso por id",
    description="Edita un curso por su id",
    request=CourseSerializer,
    responses={200: CourseSerializer,
               400: "Error al editar el curso",
               400: "El usuario no tiene el rol de coordinador",
               400: "El usuario no tiene el rol de sub-coordinador",
               404: 'Curso no encontrado'}
  )
  def put(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    
    coordinator = request.data.get('coordinator')
    if coordinator:
      rol = UserCeprunsaRoleRelation.objects.filter(idUser=coordinator, idRole=4, registerState='A').exists()
      if not rol:
        return Response({'message': f'El usuario con id {coordinator} no tiene el rol de coordinador'},
                        status=status.HTTP_400_BAD_REQUEST)
    subCoordinator = request.data.get('subCoordinator')
    if subCoordinator:
      rol = UserCeprunsaRoleRelation.objects.filter(idUser=subCoordinator, idRole=5, registerState='A').exists()
      if not rol:
        return Response({'message': f'El usuario con id {subCoordinator} no tiene el rol de sub-coordinador'},
                        status=status.HTTP_400_BAD_REQUEST)
        
    serializer = CourseSerializer(course, data=request.data)
    if serializer.is_valid():
      serializer.save()
      courseDetail = DetailedCourseSerializer(course)
      return Response(courseDetail.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  @extend_schema(
    summary="Eliminar curso por id",
    description="Elimina un curso por su id",
    responses={204: 'Curso eliminado',
               404: 'Curso no encontrado'}
  )
  def delete(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    course.registerState = '*'
    course.save()
    return Response({'message': 'Curso eliminado'}, status=status.HTTP_204_NO_CONTENT)