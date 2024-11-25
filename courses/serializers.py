from rest_framework import serializers
from courses.models import Course

class DetailedCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'coordinator', 'registerState']