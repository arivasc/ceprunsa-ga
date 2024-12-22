from rest_framework import serializers
from courses.models import Course, CourseTeacherRelation


#================================================================
# CourseSerializer para crear un nuevo curso
#================================================================

class CourseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = ['id',
              'name',
              'description',
              'coordinator',
              'subCoordinator',
              'registerState'
              ]

#================================================================
# DetailedCourseSerializer para obtener un curso con los nombres
# de los coordinadores y subcoordinadores
#================================================================
class DetailedCourseSerializer(serializers.ModelSerializer):
  
  coordinatorId = serializers.IntegerField(source='coordinator.id', read_only=True)
  coordinatorNames = serializers.SerializerMethodField()
  
  subCoordinatorId = serializers.IntegerField(source='subCoordinator.id', read_only=True)
  subCoordinatorNames = serializers.SerializerMethodField()

  class Meta:
    model = Course
    fields = [
      'id', 
      'name', 
      'description', 
      'coordinatorId', 
      'coordinatorNames', 
      'subCoordinatorId',
      'subCoordinatorNames',
      'registerState'
    ]

  def get_coordinatorNames(self, obj):
    coordinator = obj.coordinator
    if coordinator and hasattr(coordinator, 'userceprunsapersonalinfo'):
      personal_info = coordinator.userceprunsapersonalinfo
      first_name = personal_info.names.split(' ')[0]
      last_names = personal_info.lastNames.split(' ')
     
      second_name_initial = (
          personal_info.names.split(' ')[1][0] + '.'
          if len(personal_info.names.split(' ')) > 1 else ''
      )
      last_name_1 = last_names[0] if len(last_names) > 0 else ''
      last_name_2_initial = (last_names[1][0] + '.') if len(last_names) > 1 else ''
      
      formatted_name = f"{first_name} {second_name_initial} {last_name_1} {last_name_2_initial}"
      return formatted_name
    return None
  
  def get_subCoordinatorNames(self, obj):
    subCoordinator = obj.subCoordinator
    if subCoordinator and hasattr(subCoordinator, 'userceprunsapersonalinfo'):
      personal_info = subCoordinator.userceprunsapersonalinfo
      first_name = personal_info.names.split(' ')[0]
      last_names = personal_info.lastNames.split(' ')
     
      second_name_initial = (
          personal_info.names.split(' ')[1][0] + '.'
          if len(personal_info.names.split(' ')) > 1 else ''
      )
      last_name_1 = last_names[0] if len(last_names) > 0 else ''
      last_name_2_initial = (last_names[1][0] + '.') if len(last_names) > 1 else ''
      
      formatted_name = f"{first_name} {second_name_initial} {last_name_1} {last_name_2_initial}"
      return formatted_name
    return None
  
  
#================================================================
# CourseTeacherRelationSerializer para crear la relación entre
# un curso y un profesor
#================================================================
class CourseTeacherRelationSerializer(serializers.ModelSerializer):
  class Meta:
    model = CourseTeacherRelation
    fields = ['id', 'course', 'teacher']
    
#================================================================
# DetailedCourseTeacherRelationSerializer para obtener la relación
# entre un curso y un profesor con los nombres de los mismos
#================================================================
class DetailedCourseTeacherRelationSerializer(serializers.ModelSerializer):
  
  courseId = serializers.IntegerField(source='course.id', read_only=True)
  courseName = serializers.CharField(source='course.name', read_only=True)
  
  teacherId = serializers.IntegerField(source='teacher.id', read_only=True)
  teacherNames = serializers.SerializerMethodField()
  
  class Meta:
    model = CourseTeacherRelation
    fields = [
      'id',
      'courseId',
      'courseName',
      'teacherId',
      'teacherNames'
    ]
    
  def get_teacherNames(self, obj):
    teacher = obj.teacher
    if teacher and hasattr(teacher, 'userceprunsapersonalinfo'):
      personal_info = teacher.userceprunsapersonalinfo
      first_name = personal_info.names.split(' ')[0]
      last_names = personal_info.lastNames.split(' ')
     
      second_name_initial = (
          personal_info.names.split(' ')[1][0] + '.'
          if len(personal_info.names.split(' ')) > 1 else ''
      )
      last_name_1 = last_names[0] if len(last_names) > 0 else ''
      last_name_2_initial = (last_names[1][0] + '.') if len(last_names) > 1 else ''
      
      formatted_name = f"{first_name} {second_name_initial} {last_name_1} {last_name_2_initial}"
      return formatted_name
    return None