from rest_framework import serializers
from processes.models import Process

class DetailedProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'name', 'description', 'yearOfEntry', 'yearProcess', 'dateStart', 'dateEnd', 'importantDates', 'shifts', 'processType', 'registerState']
        
class SimpleListProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ['id', 'name', 'yearProcess', 'dateStart', 'dateEnd', 'registerState']