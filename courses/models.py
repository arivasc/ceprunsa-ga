from django.db import models
from userAuth.models import UserCeprunsa

class Course(models.Model):
    name = models.CharField(max_length=63, unique=True)
    description = models.CharField(max_length=255)
    coordinator = models.ForeignKey(UserCeprunsa, on_delete=models.CASCADE, blank=True, null=True)
    registerState = models.CharField(max_length=1, default='A', db_column='register_state')
    
    class Meta:
        db_table = 'courses'