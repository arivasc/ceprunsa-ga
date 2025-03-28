from rest_framework import serializers
from userAuth.models import RoleCeprunsa, UserCeprunsa, UserCeprunsaRoleRelation
from userInfo.models import UserCeprunsaPaymentInfo, UserCeprunsaPersonalInfo
from userInfo.serializers import UserCeprunsaPersonalInfoSerializer, UserCeprunsaPaymentInfoSerializer

#=============================================================================
#Serializador de crear userCeprunsa con sus roles, personalInfo y paymentInfo
#=============================================================================

class RolesCeprunsaListSerializer(serializers.PrimaryKeyRelatedField):
  def get_queryset(self):
    return RoleCeprunsa.objects.filter(registerState='A')
  
  class Meta:
    model = RoleCeprunsa
    fields = ['id', 'name', 'description', 'registerState']
  
class UserCeprunsaRolesAndInfosCreateSerializer(serializers.ModelSerializer):
  roles = RolesCeprunsaListSerializer(many=True)
  personalInfo = UserCeprunsaPersonalInfoSerializer()
  paymentInfo = UserCeprunsaPaymentInfoSerializer()
  
  class Meta:
    model = UserCeprunsa
    fields = ['email',
              'roles', 
              'personalInfo',
              'paymentInfo'
              ]
    
  def create(self, validated_data):
    roles = validated_data.pop('roles', [])
    personalInfo = validated_data.pop('personalInfo')
    paymentInfo = validated_data.pop('paymentInfo')
    
    userCeprunsa = UserCeprunsa.objects.create(**validated_data)
    
    for role_id in roles:
      role = RoleCeprunsa.objects.get(id=role_id.id)
      UserCeprunsaRoleRelation.objects.create(idUser=userCeprunsa, idRole=role)
    
    UserCeprunsaPersonalInfo.objects.create(idUserCeprunsa=userCeprunsa, **personalInfo)
    UserCeprunsaPaymentInfo.objects.create(idUserCeprunsa=userCeprunsa, **paymentInfo)
    
    return userCeprunsa


#=============================================================================
#Serializador de UserCeprunsa con sus roles, personalInfo y paymentInfo completo
#=============================================================================

class UserCeprunsaDetailSerializer(serializers.ModelSerializer):
  
  roles = serializers.SerializerMethodField()
  personalInfo = serializers.SerializerMethodField()
  paymentInfo = serializers.SerializerMethodField()

  class Meta:
    model = UserCeprunsa
    fields = ['id', 'email', 'roles', 'personalInfo', 'paymentInfo']

  def get_roles(self, obj):
    role_relations = UserCeprunsaRoleRelation.objects.filter(idUser=obj, registerState='A')
    roles = RoleCeprunsa.objects.filter(id__in=role_relations.values_list('idRole', flat=True))
    return RoleCeprunsaSerializer(roles, many=True).data

  def get_personalInfo(self, obj):
    try:
      personal_info = UserCeprunsaPersonalInfo.objects.get(idUserCeprunsa=obj)
      return UserCeprunsaPersonalInfoSerializer(personal_info).data
    except UserCeprunsaPersonalInfo.DoesNotExist:
      return None

  def get_paymentInfo(self, obj):
    try:
      payment_info = UserCeprunsaPaymentInfo.objects.get(idUserCeprunsa=obj)
      return UserCeprunsaPaymentInfoSerializer(payment_info).data
    except UserCeprunsaPaymentInfo.DoesNotExist:
      return None


#=============================================================================
#Serializador de UserCeprunsa con personalInfo y paymentInfo completo
#=============================================================================

class UserCeprunsaToEditSerializer(serializers.ModelSerializer):
  personalInfo = UserCeprunsaPersonalInfoSerializer(required=False)
  paymentInfo = UserCeprunsaPaymentInfoSerializer(required=False)

  class Meta:
    model = UserCeprunsa
    fields = ['id', 'email', 'personalInfo', 'paymentInfo']

  def update(self, instance, validated_data):
    
    instance.email = validated_data.get('email', instance.email)
    instance.save()

    personal_info_data = validated_data.get('personalInfo', None)
    if personal_info_data:
      personal_info_instance = instance.userceprunsapersonalinfo
      for key, value in personal_info_data.items():
        setattr(personal_info_instance, key, value)
      personal_info_instance.save()

    payment_info_data = validated_data.get('paymentInfo', None)
    if payment_info_data:
      payment_info_instance = instance.userceprunsapaymentinfo
      for key, value in payment_info_data.items():
        setattr(payment_info_instance, key, value)
      payment_info_instance.save()

    return instance

#=============================================================================
#Serializador de listado simple de UserCeprunsa con algunos datos personales
#=============================================================================

class RoleCeprunsaSimpleSerializer(serializers.ModelSerializer):
  class Meta:
    model = RoleCeprunsa
    fields = ['id', 'name']
    
class UserCeprunsaSimpleListSerializer(serializers.ModelSerializer):
  names = serializers.CharField(
    source='userceprunsapersonalinfo.names', read_only=True)
  lastNames = serializers.CharField(
    source='userceprunsapersonalinfo.lastNames', read_only=True)
  documentType = serializers.CharField(
    source='userceprunsapersonalinfo.documentType', read_only=True)
  identityDocument = serializers.CharField(
    source='userceprunsapersonalinfo.identityDocument', read_only=True)
  roles = serializers.SerializerMethodField()
    
  class Meta:
    model = UserCeprunsa
    fields = [
      'id',
      'roles',
      'names',
      'lastNames',
      'documentType',
      'identityDocument',
      'email',
      'registerState'
      ]
  
  def get_roles(self, obj):
    role_relations = UserCeprunsaRoleRelation.objects.filter(idUser=obj, registerState='A')
    roles = RoleCeprunsa.objects.filter(id__in=role_relations.values_list('idRole', flat=True))
    return RoleCeprunsaSimpleSerializer(roles, many=True).data


#=============================================================================
#Serializador de UserCeprunsa con algunos datos personales
#=============================================================================

class UserCeprunsaSimpleSerializer(serializers.ModelSerializer):
  names = serializers.CharField(
    source='userceprunsapersonalinfo.names', read_only=True)
  lastNames = serializers.CharField(
    source='userceprunsapersonalinfo.lastNames', read_only=True)
 
    
  class Meta:
    model = UserCeprunsa
    fields = [
      'id',
      'names',
      'lastNames',
      ]
  
#=============================================================================
#Serializador de UserCeprunsa con email y algunos datos personales
#=============================================================================

class UserCeprunsaSimpleSerializer(serializers.ModelSerializer):
  names = serializers.CharField(
    source='userceprunsapersonalinfo.names', read_only=True)
  lastNames = serializers.CharField(
    source='userceprunsapersonalinfo.lastNames', read_only=True)
 
    
  class Meta:
    model = UserCeprunsa
    fields = [
      'id',
      'email',
      'names',
      'lastNames',
      ]
 

#=============================================================================
#Serializador de UserCeprunsa con sus roles, personalInfo y paymentInfo resumido
#=============================================================================

class PersonalInfoResumeSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserCeprunsaPersonalInfo
    fields = ['names', 'lastNames']

class PaymentInfoResumeSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserCeprunsaPaymentInfo
    fields = ['universityRelationship']
    
class RolCeprunsaResumeSerializer(serializers.ModelSerializer):
  def get_queryset(self):
    return RoleCeprunsa.objects.filter(registerState='A')
  class Meta:
    model = RoleCeprunsa
    fields = ['id', 'name']

class UserCeprunsaResumeSerializer(serializers.ModelSerializer):
  personalInfo = PersonalInfoResumeSerializer()
  paymentInfo = PaymentInfoResumeSerializer()
  roles = RolCeprunsaResumeSerializer(many=True)
  
  class Meta:
    model = UserCeprunsa
    fields = ['id', 'email', 'roles', 'personalInfo', 'paymentInfo']


#=============================================================================
#Serializadores de relacion de roles con usuarios
#=============================================================================

class UserCeprunsaRolRelationSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = UserCeprunsaRoleRelation
    fields = ['id', 'idUser', 'idRole', 'registerState']
    
  def validate_idUser(self, value):
    if not UserCeprunsa.objects.filter(id=value.id).exists():
      raise serializers.ValidationError("El usuario especificado no existe.")
    return value

  def validate_idRole(self, value):
    if not RoleCeprunsa.objects.filter(id=value.id).exists():
      raise serializers.ValidationError("El rol especificado no existe.")
    return value


#=============================================================================
#Serializador de solicitud de asignacion de roles a un usuario
#=============================================================================
class UserRoleAssignmentRequestSerializer(serializers.Serializer):
  roles = serializers.ListField(
    child=serializers.IntegerField(),
    min_length=1,
    max_length=2,
    help_text="Lista de IDs de roles (mínimo 1, máximo 2)"
  )


#=============================================================================
#Serializador de solicitud de refrescar token
#=============================================================================
class RefreshTokenRequestSerializer(serializers.Serializer):
  refresh = serializers.CharField(
    help_text="El token de refresco proporcionado por el servidor",
  )



#=============================================================================

class RoleCeprunsaSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = RoleCeprunsa
    fields = ['id', 'name','description', 'registerState']
    
class UserCeprunsaSerializer(serializers.ModelSerializer):
    
  class Meta:
    model = UserCeprunsa
    fields = ['id', 'email', 'is_staff', 'is_superuser', 'joinDate', 'registerState']



   
class UserCeprunsaSimple2Serializer(serializers.ModelSerializer):
  class Meta:
    model = UserCeprunsa
    fields = ['id', 'email', 'registerState']   