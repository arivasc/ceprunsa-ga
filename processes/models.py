from django.db import models
import json

class Process(models.Model):
  name = models.CharField(max_length=63, unique=True)
  description = models.CharField(max_length=100)
  yearOfEntry = models.CharField(max_length=4, db_column='year_of_entry')
  yearProcess = models.CharField(max_length=4, db_column='year_process')
  dateStart = models.DateField(db_column='date_start')
  dateEnd = models.DateField(db_column='date_end')
  importantDates = models.TextField(db_column='important_dates')
  shifts = models.TextField()
  processType = models.CharField(max_length=1, db_column='process_type')
  registerState = models.CharField(max_length=1, default='A', db_column='register_state')
  
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