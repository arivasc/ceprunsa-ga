from django.db import models
from userAuth.models import UserCeprunsa

class UserCeprunsaPersonalInfo(models.Model):
  idUserCeprunsa = models.OneToOneField(UserCeprunsa, on_delete=models.CASCADE, db_column='id_user_ceprunsa')
  names = models.CharField(max_length=100, db_column='first_names')
  lastNames = models.CharField(max_length=100, db_column='last_names')
  birthDate = models.DateField(db_column='birth_date', blank=True, null=True)
  phone = models.CharField(max_length=15, db_column='main_phone')
  address = models.CharField(max_length=100, blank=True, null=True)
  documentType = models.CharField(max_length=3, db_column='document_type', default='DNI')
  identityDocument = models.CharField(max_length=12, db_column='identity_document')
  secondPhone = models.CharField(max_length=15, db_column='second_phone', blank=True, null=True)
  personalEmail = models.EmailField(max_length=100, db_column='personal_email', blank=True, null=True)
  cv = models.FileField(upload_to='cv/', db_column='cv', blank=True, null=True)
  academicDegree = models.CharField(max_length=100, db_column='academic_degree', blank=True, null=True)
  career = models.TextField(blank=True, null=True)

  class Meta:
    db_table = 'personal_informations'
    
class UserCeprunsaPaymentInfo(models.Model):
  idUserCeprunsa = models.OneToOneField(UserCeprunsa, on_delete=models.CASCADE, db_column='id_user_ceprunsa')
  universityRelationship = models.CharField(max_length=1, db_column='university_relationship')
  ruc = models.CharField(max_length=11, blank=True, null=True)
  bankEntity = models.CharField(max_length=100, blank=True, null=True, db_column='bank_entity')
  bankAccount = models.CharField(max_length=20, blank=True, null=True, db_column='bank_account')
  cci = models.CharField(max_length=20, blank=True, null=True)
  hasFourthSuspension = models.BooleanField(default=False, db_column='has_fourth_suspension')

  class Meta:
    db_table = 'payment_informations'