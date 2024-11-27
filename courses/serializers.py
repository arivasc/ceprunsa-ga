from rest_framework import serializers
from courses.models import Course

class CourseSerializer(serializers.ModelSerializer):
  class Meta:
    model = Course
    fields = ['id', 'name', 'description', 'coordinator', 'registerState']


class DetailedCourseSerializer(serializers.ModelSerializer):
  
  coordinatorId = serializers.IntegerField(source='coordinator.id', read_only=True)
  coordinatorNames = serializers.SerializerMethodField()

  class Meta:
    model = Course
    fields = [
      'id', 
      'name', 
      'description', 
      'coordinatorId', 
      'coordinatorNames', 
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