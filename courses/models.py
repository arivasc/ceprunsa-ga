from django.db import models
from userAuth.models import UserCeprunsa

class Course(models.Model):
    name = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    coordinator = models.ForeignKey(
        UserCeprunsa, on_delete=models.CASCADE,
        blank=True, null=True,
        related_name='coordinator')
    subCoordinator = models.ForeignKey(
        UserCeprunsa, on_delete=models.CASCADE,
        blank=True, null=True,
        db_column='sub_coordinator',
        related_name='subCoordinator')
    registerState = models.CharField(max_length=1, default='A', db_column='register_state')
    
    class Meta:
        db_table = 'courses'
        

class CourseTeacherRelation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher = models.ForeignKey(UserCeprunsa, on_delete=models.CASCADE)
    
    class Meta:
        db_table = 'course_teacher_relation'