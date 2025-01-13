from rest_framework import serializers
from processes.models import Process, ProcessUserCerprunsaRelation
import json

#================================================================
# ProcessUserCerprunsaRelationSerializer para crear una relación
# entre un usuario y un proceso
#================================================================
class ProcessUserCerprunsaRelationSerializer(serializers.ModelSerializer):
  class Meta:
    model = ProcessUserCerprunsaRelation
    fields = [
      'id',
      'idUserCeprunsa',
      'idProcess',
      'idRole',
      'startDate',
      'endDate',
      'idCourse',
      'weekHours',
      'totalHours',
      'paymentType',
      'finalState',
      'quality',
      'registerState'
      ]
    
#================================================================
# ProcessUserCerprunsaRelationDetailSerializer para ver en detalle
# la relacion entre usuario y proceso
#================================================================
class ProcessUserCerprunsaRelationDetailSerializer(serializers.ModelSerializer):
  
  userNames = serializers.SerializerMethodField()
  processName = serializers.CharField(source='idProcess.name', read_only=True)
  roleName = serializers.CharField(source='idRole.name', read_only=True)
  courseName = serializers.SerializerMethodField()
  
  class Meta:
    model = ProcessUserCerprunsaRelation
    fields = [
      'id',
      'idUserCeprunsa',
      'userNames',
      'idProcess',
      'processName',
      'idRole',
      'roleName',
      'startDate',
      'endDate',
      'idCourse',
      'courseName',
      'weekHours',
      'totalHours',
      'paymentType',
      'finalState',
      'quality',
      'registerState'
      ]
  
  def get_userNames(self, obj):
    user = obj.idUserCeprunsa
    if user and hasattr(user, 'userceprunsapersonalinfo'):
      personal_info = user.userceprunsapersonalinfo
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

  def get_courseName(self, obj):
    
    return obj.idCourse.name if obj.idCourse else None

#================================================================
# ProcessUserCerprunsaRelationListSerializer para listar las
# relaciones entre usuarios y un proceso
#================================================================
class ProcessUserCerprunsaRelationsListSerializer(serializers.ModelSerializer):
  
  userNames = serializers.SerializerMethodField()
  #processName = serializers.CharField(source='idProcess.name', read_only=True)
  roleName = serializers.CharField(source='idRole.name', read_only=True)
  courseName = serializers.SerializerMethodField()
  
  class Meta:
    model = ProcessUserCerprunsaRelation
    fields = [
      'id',
      'idUserCeprunsa',
      'userNames',
      'idRole',
      'roleName',
      'idCourse',
      'courseName',
      'registerState'
      ]
  
  def get_userNames(self, obj):
    user = obj.idUserCeprunsa
    if user and hasattr(user, 'userceprunsapersonalinfo'):
      personal_info = user.userceprunsapersonalinfo
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

  def get_courseName(self, obj):
    
    return obj.idCourse.name if obj.idCourse else None


#================================================================
# ProcessSerializer para crear y ver un nuevo proceso
#================================================================

class DetailedProcessSerializer(serializers.ModelSerializer):
  class Meta:
    model = Process
    fields = [
      'id',
      'name',
      'description',
      'yearOfEntry',
      'yearProcess',
      'dateStart',
      'dateEnd',
      'importantDates',
      'shifts',
      'processType',
      'registerState'
      ]
  
  # Convertir JSON a string antes de guardar
  def to_internal_value(self, data):
    data['importantDates'] = json.dumps(data.get('importantDates', {}))
    data['shifts'] = json.dumps(data.get('shifts', {}))
    return super().to_internal_value(data)
  
  # Convertir string a JSON al devolver los datos
  def to_representation(self, instance):
    representation = super().to_representation(instance)
    representation['importantDates'] = json.loads(instance.importantDates)
    representation['shifts'] = json.loads(instance.shifts)
    return representation
        
#================================================================
# SimpleListProcessSerializer para listar procesos
#================================================================      
class SimpleListProcessSerializer(serializers.ModelSerializer):
  class Meta:
    model = Process
    fields = ['id', 'name', 'yearProcess', 'dateStart', 'dateEnd', 'registerState']