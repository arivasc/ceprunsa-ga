from rest_framework import serializers
from userInfo.models import UserCeprunsaPersonalInfo, UserCeprunsaPaymentInfo

class UserCeprunsaPersonalInfoSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserCeprunsaPersonalInfo
    fields = [
      'id',
      'names', 
      'lastNames', 
      'birthDate', 
      'phone', 
      'address', 
      'documentType', 
      'identityDocument', 
      'secondPhone',
      'personalEmail',
      'cv',
      'academicDegree',
      'career'
      ]
    
class UserCeprunsaPaymentInfoSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserCeprunsaPaymentInfo
    fields = [
      'id',
      'universityRelationship',
      'ruc',
      'bankEntity',
      'bankAccount',
      'cci',
      'hasFourthSuspension'
      ]