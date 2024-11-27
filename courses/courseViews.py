from courses.models import Course
from courses.serializers import DetailedCourseSerializer, CourseSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from drf_spectacular.utils import extend_schema

#==============================================================================
#API para listar y crear cursos
#==============================================================================

class CourseCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Crear curso",
    description="Crea un curso con sus datos",
    request=CourseSerializer,
    responses={201: CourseSerializer}
  )
  def post(self, request):
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
    responses={200: DetailedCourseSerializer}
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
    responses={200: CourseSerializer}
  )
  def put(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = CourseSerializer(course, data=request.data)
    if serializer.is_valid():
      serializer.save()
      courseDetail = DetailedCourseSerializer(course)
      return Response(courseDetail.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  @extend_schema(
    summary="Eliminar curso por id",
    description="Elimina un curso por su id",
    responses={204: 'Curso eliminado'}
  )
  def delete(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    course.registerState = '*'
    course.save()
    return Response({'message': 'Curso eliminado'}, status=status.HTTP_204_NO_CONTENT)