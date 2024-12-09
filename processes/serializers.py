from rest_framework import serializers
from processes.models import Process
import json

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
        
        
class SimpleListProcessSerializer(serializers.ModelSerializer):
  class Meta:
    model = Process
    fields = ['id', 'name', 'yearProcess', 'dateStart', 'dateEnd', 'registerState']