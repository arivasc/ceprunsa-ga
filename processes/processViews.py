from django.utils import timezone
from django.http import HttpResponse
from processes.generateReportXlsx import generateReportProcess, generateExcelReportUsersInProcessByRole
from processes.models import Process, ProcessUserCeprunsaRelation
from userAuth.models import UserCeprunsa, UserCeprunsaRoleRelation
from courses.models import CourseTeacherRelation, Course
from userInfo.models import UserCeprunsaPersonalInfo
from processes.serializers import (
  DetailedProcessSerializer,
  SimpleListProcessSerializer,
  ProcessUserCeprunsaRelationsListSerializer,
  ProcessUserCeprunsaRelationSerializer,
  ProcessUserCeprunsaRelationDetailSerializer,
  ProcessUserCeprunsaListSerializer)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

#==============================================================================
#API para cambiar el estado de un proceso
#==============================================================================
class ProcessStateChangeView(APIView):
  #permission_classes = [IsAuthenticated]
  @extend_schema(
    summary="Cambiar estado de un proceso",
    description="Cambia el estado de un proceso a uno nuevo especificado.",
    request={
      "application/json": {
        "type": "object",
        "properties": {
          "newState": {
            "type": "string",
            "description": "Nuevo estado del proceso.",
          },
        },
        "required": ["newState"],
        "example": {"newState": "C"},
      }
    },
    responses={200: {"message": "Estado del proceso modificado"},
               404: {"message": "Proceso no encontrado"},
               400: {"message": "Debe especificar un nuevo estado"}}
  )
  def post(self, request, pk):
    
    process = Process.objects.get(id=pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    newState = request.data.get('newState', 'Z').upper()
    if newState == 'Z':
      return Response({'message': 'Debe especificar un nuevo estado'},
                      status=status.HTTP_400_BAD_REQUEST
      )
    else:
      process.registerState = newState
      process.save()
      return Response({'message': 'Estado del proceso modificado'}, status=status.HTTP_200_OK)

#==============================================================================
#API para listar los procesos de un usuario
#==============================================================================
class ProcessUserCeprunsaListView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Mostrar procesos de un usuario",
    description="Muestra todos los procesos de un usuario. Envia el id del usuario como parámetro. url/id",
    responses={200: ProcessUserCeprunsaListSerializer(many=True),
               404: "No hay procesos para este usuario"},
    
  )
  def get(self, request, pk):
        
    try:
      relations = ProcessUserCeprunsaRelation.objects.filter(idUserCeprunsa=pk).exclude(registerState='*')
    except ObjectDoesNotExist:
      return Response({'message': 'No hay procesos para este usuario'}, status=status.HTTP_404_NOT_FOUND)
    
    if not relations:
      return Response({'message': 'No hay procesos para este usuario'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProcessUserCeprunsaListSerializer(relations, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

#==============================================================================
#API para listar y crear relaciones entre usuarios y procesos
#==============================================================================
class ProcessUserCeprunsaRelationListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Mostrar relaciones usuarios-proceso",
    description="Muestra todas las relaciones entre usuarios y un proceso."
    "\n\nPara obtener solo relaciones relacionadas a un usuario, se debe usar ?userId=#. Esto ignorará el parámetro pk, tampoco usar los demás parámetros."
    "\n\nPara incluir relaciones eliminadas, se debe especificar '?includeAll=true'"
    "\n\nPara incluir roles usar ?role=#."
    "\n\nPara buscar por nombre o apellido usar ?search=cadena"
    "\n\nPara usar varios parámetros, separarlos con &.",
    responses={200: ProcessUserCeprunsaRelationsListSerializer(many=True),
               404: "No hay relaciones para este proceso con los parámetros dados",
               404: "No se encontraron relaciones con ese id de usuario"},
    parameters=[
      OpenApiParameter(
        name='role',
        required=False,
        description='valores aceptados: 1-8',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='role',
            value=''
          )
        ]
      ),
      OpenApiParameter(
        name='search',
        required=False,
        description='valores aceptados: nombres o apellidos',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='search',
            value=''
          )
        ]
      ),
      OpenApiParameter(
        name='userId',
        required=False,
        description='valores aceptados: userId',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='userId',
            value=''
          )
        ]
      ),
      OpenApiParameter(
        name='excel',
        required=False,
        description='valores aceptados: true / false',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='excel',
            value='false'
          )
        ]
      )
    ]
  )
  def get(self, request, pk):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
    role = request.query_params.get('role', None)
    search = request.query_params.get('search', None)
    userId = request.query_params.get('userId', None)
    excel = request.query_params.get('excel', 'false').lower() == 'true'
    if excel:
      try:
        relations = ProcessUserCeprunsaRelation.objects.filter(idProcess=pk, idRole=role).exclude(registerState='*')
        if not relations:
          return Response({'message': 'No hay relaciones para este proceso con los parámetros dados'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProcessUserCeprunsaRelationsListSerializer(relations, many=True)
        excel_file = generateExcelReportUsersInProcessByRole(serializer.data)
        current_date = timezone.now().strftime("%d-%m-%Y_%H%M%S")
        roleName = ProcessUserCeprunsaRelation.objects.filter(idRole=role).first().idRole.name
        if role == '6':
          roleName = 'Servidor de Ense'
        processName = Process.objects.get(id=pk).name
        filename = f"{roleName} - {processName} _{current_date}.xlsx"
        response = HttpResponse(
          excel_file.getvalue(),
          content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
      except ObjectDoesNotExist:
        return Response({'message': 'No se encontraron relaciones para este proceso con el rol dado'}, status=status.HTTP_404_NOT_FOUND)
      
    else:
    
      if includeAll:
        relations = ProcessUserCeprunsaRelation.objects.filter(idProcess=pk)
      elif userId:
        try:
          relations = ProcessUserCeprunsaRelation.objects.filter(idUserCeprunsa=userId)
        except ObjectDoesNotExist:
          return Response({'message': 'No se encontraron relaciones con ese id de usuario'}, status=status.HTTP_404_NOT_FOUND)
      else:
        relations = ProcessUserCeprunsaRelation.objects.filter(idProcess=pk).exclude(registerState='*')
        
      if role:
        relations = relations.filter(idRole=role)
      
      if search:
        relations = relations.filter(
          idUserCeprunsa__userceprunsapersonalinfo__names__icontains=search
          ) | relations.filter(
          idUserCeprunsa__userceprunsapersonalinfo__lastNames__icontains=search
          )
      
      if not relations:
        return Response({'message': 'No hay relaciones para este proceso con los parámetros dados'}, status=status.HTTP_404_NOT_FOUND)
      pagination = PageNumberPagination()
      pagination.page_size = 30
      
      paginatedUsers = pagination.paginate_queryset(relations, request)
      
      serializer = ProcessUserCeprunsaRelationsListSerializer(paginatedUsers, many=True)
      
      return pagination.get_paginated_response(serializer.data)
  
  @extend_schema(
    summary="Asignar usuarios a un proceso",
    description=(
        "Asigna uno o más usuarios a un proceso especificado por su ID (pk). "
        "El usuario debe tener roles activos asignados, y la relación no debe existir previamente. "
        "Además, se puede proporcionar un nivel de calidad opcional para la relación. "
        "Los usuarios sin roles activos o relaciones ya existentes generan errores."
    ),
    request={
      "application/json": {
        "type": "object",
        
        "required": ["relations"],
        "example": {"relations": [{
          "userId":1,
          "quality": "2"}]
                    },
      }
    },
    responses={
        201: OpenApiExample(
            "Asignaciones exitosas",
            value={
                "created": [
                    {
                        "id": 1,
                        "idUserCeprunsa": 5,
                        "idProcess": 10,
                        "idRole": 2,
                        "idCourse": None,
                        "startDate": "2024-01-01",
                        "endDate": "2024-12-31",
                        "quality": "Alta",
                    }
                ],
                "errors": [],
            },
        ),
        400: OpenApiExample(
            "Errores en las asignaciones",
            value={
                "created": [],
                "errors": [
                    "El usuario con id 3 no tiene roles asignados",
                    "El usuario con id 5 ya tiene una relación con el proceso CEPRUNSA y el rol Docente",
                ],
            },
        ),
    },
    examples=[
        OpenApiExample(
            "Ejemplo de solicitud",
            value={"relations": [
              {
                "userId":1,
                "quality": "2"
              }
              ]
                    },
            request_only=True,
        ),
    ],
  )
  def post(self, request, pk):
    process = Process.objects.get(id=pk)
    relations = request.data.get('relations', [])
    
    if not isinstance(relations, list) or not relations:
      return Response({'message': 'Debe asignar al menos un usuario'}, status=status.HTTP_400_BAD_REQUEST)
    
    createdRelations = []
    errors = []
    
    for relation in relations:
      if not isinstance(relation, dict) or 'userId' not in relation:
        errors.append('Cada relación debe tener un campo "userId"')
        continue
      
      userId = relation['userId']
      quality = relation.get('quality', 'A')
      
      try:
        user = UserCeprunsa.objects.get(id=userId, registerState='A')
        print(user.email)
        hasRoles = UserCeprunsaRoleRelation.objects.filter(idUser=user, registerState='A')
        
        
        if not hasRoles:
          print()
          names = UserCeprunsaPersonalInfo.objects.get(
            idUserCeprunsa=userId).names + " " + UserCeprunsaPersonalInfo.objects.get(
              idUserCeprunsa=userId).lastNames
          errors.append(f'El usuario con id {userId} y nombres {names} no tiene roles asignados')
          continue
        
        for role in hasRoles:
          relation = ProcessUserCeprunsaRelation.objects.filter(idUserCeprunsa=user, idProcess=process, idRole=role.idRole)
          
          if relation:
            names = UserCeprunsaPersonalInfo.objects.get(
              idUserCeprunsa=userId).names + " " + UserCeprunsaPersonalInfo.objects.get(
                idUserCeprunsa=userId).lastNames
            errors.append(f'El usuario con id {userId} y nombres {names} ya tiene una relación con el proceso {process.name} con el rol {role.idRole.name}')
            continue
          
          course = None
          if role.idRole.name == 'Servidor de Enseñanza':
            courseRelation = CourseTeacherRelation.objects.filter(idTeacher=user)
            
            if not courseRelation:
              names = UserCeprunsaPersonalInfo.objects.get(
              idUserCeprunsa=userId).names + " " + UserCeprunsaPersonalInfo.objects.get(
                idUserCeprunsa=userId).lastNames
              errors.append(f'El usuario con id {userId}, nombres {names} y rol {role.idRole.name} no tiene un curso asignado')
              continue
            
            else:
              idCourse = CourseTeacherRelation.objects.get(idTeacher=user).idCourse
              course = Course.objects.get(id=idCourse.id)
          
          elif role.idRole.name == 'Coordinador' or role.idRole.name == 'Sub Coordinador':
            course = Course.objects.get(idCoordinator=user) if Course.objects.get(idCoordinator=user) else Course.objects.get(idSubCoordinator=user)
            if not course:
              names = UserCeprunsaPersonalInfo.objects.get(
              idUserCeprunsa=userId).names + " " + UserCeprunsaPersonalInfo.objects.get(
                idUserCeprunsa=userId).lastNames
              errors.append(f'El usuario con id {userId}, nombres {names} y rol {role.idRole.name} no tiene un curso asignado')
              continue
          
          
          
          relation = ProcessUserCeprunsaRelation.objects.create(
            idUserCeprunsa=user,
            idProcess=process,
            idRole=role.idRole,
            idCourse= course,
            startDate = process.dateStart,
            endDate = process.dateEnd,
            quality=quality
          )
          createdRelations.append(relation)
            
      except ObjectDoesNotExist:
        errors.append(f'El usuario con id {userId} no existe')
    serializer = ProcessUserCeprunsaRelationSerializer(createdRelations, many=True)
    return Response(
      {'created': serializer.data,
       'errors': errors},
      status=status.HTTP_201_CREATED if createdRelations else status.HTTP_400_BAD_REQUEST)

#==============================================================================
#API para ver, editar y eliminar relaciones entre usuarios y procesos por id
#==============================================================================
class ProcessUserCeprunsaRelationDetailView(APIView):
  #permission_classes = [IsAuthenticated]
  
  #método para obtener una relación por id reusable
  def get_object(self, pk):
    try:
      return ProcessUserCeprunsaRelation.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de una relación por id
  @extend_schema(
    summary="Ver relación por id",
    description="Muestra una relación entre usuario y proceso con sus datos.",
    responses={200: ProcessUserCeprunsaRelationDetailSerializer}
  )
  def get(self, request, pk):
    relation = self.get_object(pk)
    if not relation:
      return Response({'message': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProcessUserCeprunsaRelationDetailSerializer(relation)
    return Response(serializer.data)
  
  #actualización de una relación por id
  @extend_schema(
    summary="Editar relación por id",
    description="Edita una relación entre usuario y proceso con sus datos.",
    request=ProcessUserCeprunsaRelationSerializer,
    responses={200: ProcessUserCeprunsaRelationSerializer}
  )
  def put(self, request, pk):
    relation = self.get_object(pk)
    if not relation:
      return Response({'message': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProcessUserCeprunsaRelationSerializer(relation, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de una relación por id
  @extend_schema(
    summary="Eliminar relación por id",
    description="Elimina una relación entre usuario y proceso.",
    responses={204: 'No Content'}
  )
  def delete(self, request, pk):
    relation = self.get_object(pk)
    if not relation:
      return Response({'message': 'Relación no encontrada'}, status=status.HTTP_404_NOT_FOUND)
    relation.registerState = '*'
    relation.save()
    return Response(status=status.HTTP_204_NO_CONTENT)



#==============================================================================
#API para listar y crear procesos
#==============================================================================

class ProcessListCreateView(APIView):
  #permission_classes = [IsAuthenticated]
  
  @extend_schema(
    summary="Mostrar procesos",
    description="Muestra todos los procesos registrados.",
    
    responses={200: DetailedProcessSerializer(many=True)},
    parameters=[
      OpenApiParameter(
        name='excel',
        required=False,
        description='valores aceptados: true o false',
        type=str,
        location='query',
        examples=[
          OpenApiExample(
            name='excel',
            value='true'
          )
        ]
      )
    ]
  )
  def get(self, request):
    includeAll = request.query_params.get('includeAll', 'false').lower() == 'true'
    excel = request.query_params.get('excel', 'false').lower() == 'true'
      
    if includeAll:
      processes = Process.objects.all()
    else:
      #filter = request.query_params.get('filter', 'A').upper()        
      processes = Process.objects.exclude(registerState='*')
    
    if excel:
      excel_file = generateReportProcess(processes)
      current_date = timezone.now().strftime('%d-%m-%Y')
      filename = f"Lista de Procesos_{current_date}.xlsx"
      response = HttpResponse(
        excel_file.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      response['Content-Disposition'] = f'attachment; filename={filename}'
      return response
      
    serializer = SimpleListProcessSerializer(processes, many=True)
    return Response(serializer.data)
  
  @extend_schema(
    summary="Crear proceso",
    description="Crea un proceso con sus datos.",
    request=DetailedProcessSerializer,
    responses={201: DetailedProcessSerializer}
  )  
  def post(self, request):
    serializer = DetailedProcessSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#==============================================================================
#API para ver, editar y eliminar procesos por id
#==============================================================================

class ProcessDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  #método para obtener un proceso por id reusable
  def get_object(self, pk):
    try:
      return Process.objects.get(id=pk)
    except ObjectDoesNotExist:
      return None
  
  #obtención de un proceso por id
  @extend_schema(
    summary="Ver proceso por id",
    description="Muestra un proceso con sus datos.",
    responses={200: DetailedProcessSerializer}
  )
  def get(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process)
    return Response(serializer.data)
  
  #actualización de un proceso por id
  @extend_schema(
    summary="Editar proceso por id",
    description="Edita un proceso con sus datos.",
    request=DetailedProcessSerializer,
    responses={200: DetailedProcessSerializer}
  )
  def put(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    serializer = DetailedProcessSerializer(process, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
  
  #eliminación de un proceso por id
  @extend_schema(
    summary="Eliminar proceso por id",
    description="Elimina un proceso.",
    responses={204: 'No Content'}
  )
  def delete(self, request, pk):
    process = self.get_object(pk)
    if not process:
      return Response({'message': 'Proceso no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    process.registerState = '*'
    process.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

