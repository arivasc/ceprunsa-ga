from django.db import models
from userAuth.models import UserCeprunsa, RoleCeprunsa
from courses.models import Course
import json

class Process(models.Model):
  name = models.CharField(max_length=63, unique=True)
  description = models.TextField()
  yearOfEntry = models.CharField(max_length=4, db_column='year_of_entry')
  yearProcess = models.CharField(max_length=4, db_column='year_process')
  dateStart = models.DateField(db_column='date_start')
  dateEnd = models.DateField(db_column='date_end')
  importantDates = models.TextField(db_column='important_dates')
  shifts = models.TextField()
  processType = models.CharField(max_length=1, db_column='process_type')
  registerState = models.CharField(max_length=1, default='P', db_column='register_state')
  
  def clean(self):
    for field in ['importantDates', 'shifts']:
      value = getattr(self, field, None)
      if value:
        try:
          json.loads(value)
        except json.JSONDecodeError:
          raise ValueError(
            {field: f'El campo {field} debe ser un JSON válido.'}
            )
  
  class Meta:
    db_table = 'processes'
    
class ProcessUserCeprunsaRelation(models.Model):
  idProcess = models.ForeignKey(
    Process,
    on_delete=models.CASCADE,
    db_column='id_process')
  idUserCeprunsa = models.ForeignKey(
    UserCeprunsa,
    on_delete=models.CASCADE,
    db_column='id_user_ceprunsa')
  idRole = models.ForeignKey(
    RoleCeprunsa,
    on_delete=models.CASCADE,
    db_column='id_role')
  startDate = models.DateField(db_column='start_date')
  endDate = models.DateField(db_column='end_date')
  idCourse = models.ForeignKey(
    Course,
    on_delete=models.CASCADE,
    blank=True, null=True,
    db_column='id_course')
  weekHours = models.CharField(max_length=7, db_column='week_hours', blank=True, null=True)
  totalHours = models.CharField(max_length=7, db_column='total_hours', blank=True, null=True)
  paymentType = models.CharField(max_length=2, default="RH", db_column='payment_type')
  finalState = models.CharField(max_length=1, default='E', db_column='final_state')
  quality = models.CharField(max_length=1, default='A')
  registerState = models.CharField(max_length=1, default='A', db_column='register_state')
  
  class Meta:
    db_table = 'process_user_ceprunsa_relations'
    

class Observation(models.Model):
  idProcessUserCeprunsaRelation = models.ForeignKey(
    ProcessUserCeprunsaRelation,
    on_delete=models.CASCADE,
    db_column='id_process_user_ceprunsa_relation')
  date = models.DateField()
  lastEditDate = models.DateField(blank=True, null=True, db_column='last_edit_date')
  observation = models.TextField()
  idRegisterBy = models.ForeignKey(
    UserCeprunsa,
    on_delete=models.CASCADE,
    related_name='register_by',
    db_column='id_register_by')
  idLastEditedBy = models.ForeignKey(
    UserCeprunsa,
    on_delete=models.CASCADE,
    blank=True, null=True,
    related_name='last_edited_by',
    db_column='id_last_edited_by')
  document = models.FileField(upload_to='observations/', blank=True, null=True)
  registerState = models.CharField(max_length=1, default='N', db_column='register_state')
  
  class Meta:
    db_table = 'observations'