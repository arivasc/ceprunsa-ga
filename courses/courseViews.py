from courses.models import Course
from courses.serializers import DetailedCourseSerializer
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView

class CourseCreateView(APIView):
  def post(self, request):
    serializer = DetailedCourseSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
    if includeAll:
      courses = Course.objects.all()
    else:
      filter = request.query_params.get('filter', 'A').upper()
      courses = Course.objects.select_related('coordinator__userceprunsapersonalinfo').filter(registerState=filter)
    
    serializer = DetailedCourseSerializer(courses, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
  
class CourseDetailView(APIView):
  def get_object(self, pk):
    try:
      return Course.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  def get(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedCourseSerializer(course)
    return Response(serializer.data)
  
  def put(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedCourseSerializer(course, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  def delete(self, request, pk):
    course = self.get_object(pk)
    if not course:
      return Response({'message': 'Curso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    course.delete()
    return Response({'message': 'Curso eliminado'}, status=status.HTTP_204_NO_CONTENT)