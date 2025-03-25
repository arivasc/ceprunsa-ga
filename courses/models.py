from django.db import models
from userAuth.models import UserCeprunsa

class Course(models.Model):
    name = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    idCoordinator = models.OneToOneField(
        UserCeprunsa, on_delete=models.CASCADE,
        blank=True, null=True,
        db_column='id_coordinator',
        related_name='idCoordinator')
    idSubCoordinator = models.OneToOneField(
        UserCeprunsa, on_delete=models.CASCADE,
        blank=True, null=True,
        db_column='id_sub_coordinator',
        related_name='idSubCoordinator')
    registerState = models.CharField(max_length=1, default='A', db_column='register_state')
    
    class Meta:
        db_table = 'courses'
        

class CourseTeacherRelation(models.Model):
    idCourse = models.ForeignKey(Course, on_delete=models.CASCADE, db_column='id_course')
    idTeacher = models.ForeignKey(UserCeprunsa, on_delete=models.CASCADE, db_column='id_teacher')
    
    class Meta:
        db_table = 'course_teacher_relations'