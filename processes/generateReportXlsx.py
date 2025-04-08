from openpyxl import Workbook
from io import BytesIO

USER_PROCESS_HEADER = [
  'ID',
  'Nombres',
  'Apellidos',
  'Número de documento',
  'Correo electrónico',
  'Curso'
]

REGISTER_STATE_MAP = {
  'A': 'Activo',
  'I': 'Inactivo',
  'P': 'Pendiente',
  'T': 'Terminado',
  'S': 'Suspendido',
  'C': 'Cancelado'  
}
fields = [
      'id',
      'idUserCeprunsa',
      'email',
      'userNames',
      'userLastNames',
      'identityDocument',
      'idRole',
      'roleName',
      'idCourse',
      'courseName',
      'registerState'
      ]
def generateExcelReportUsersInProcessByRole(users):
  wb = Workbook()
  ws = wb.active
  
  headers = USER_PROCESS_HEADER
  ws.append(headers)
  
  for user in users:
    row = [
      user.get('idUserCeprunsa'),
      user.get('userNames'),
      user.get('userLastNames'),
      user.get('identityDocument'),
      user.get('email'),
      user.get('courseName')
    ]
    
    ws.append(row)
  
  excelFile = BytesIO()
  wb.save(excelFile)
  excelFile.seek(0)
  
  return excelFile



#===============================================================================
# Function que genera un reporte en formato xlsx de los procesos de la base de datos
# processes: Lista de objetos de tipo Process
# return: BytesIO
#   Archivo en formato xlsx
#===============================================================================
def generateReportProcess(processes):
  wb = Workbook()
  ws = wb.active
  
  headers = [
    'ID',
    'Nombre',
    'Descripción',
    'Año de ingreso',
    'Año de proceso',
    'Fecha de inicio',
    'Fecha de fin',
    'Fechas importantes',
    'Turnos',
    'Tipo de proceso',
    'Estado del Proceso'
  ]
  
  ws.append(headers)
  
  for process in processes:
    row = [
      process.id,
      process.name,
      process.description,
      process.yearOfEntry,
      process.yearProcess,
      process.dateStart,
      process.dateEnd,
      process.importantDates,
      process.shifts,
      process.processType,
      REGISTER_STATE_MAP.get(process.registerState, 'Desconocido')
    ]
    
    ws.append(row)
    
  
  excel_file = BytesIO()
  wb.save(excel_file)
  excel_file.seek(0)
  
  return excel_file