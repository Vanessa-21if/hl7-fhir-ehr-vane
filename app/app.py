from fastapi import FastAPI, HTTPException, Request, status
import uvicorn
from app.controlador.PatientCrud import (
    GetPatientById,
    WritePatient,
    GetPatientByIdentifier,
    RegisterMedicationDispense,
    GetPatientMedications
)
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel

app = FastAPI(
    title="Sistema de Salud - Historia Clínica Electrónica",
    description="API para gestión de pacientes y registro de medicamentos FHIR",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hl7-patient-write-vanessa.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Modelos Pydantic para validación
class MedicationDispenseCreate(BaseModel):
    medication: str
    quantity: float
    daysSupply: float
    dosage: str
    performer: str
    notes: Optional[str] = None
    timestamp: Optional[datetime] = None

@app.get("/patient/{patient_id}", 
         response_model=dict,
         summary="Obtener paciente por ID",
         responses={
             404: {"description": "Paciente no encontrado"},
             500: {"description": "Error interno del servidor"}
         })
async def get_patient_by_id(patient_id: str):
    """
    Obtiene los datos completos de un paciente por su ID
    
    - **patient_id**: ID único del paciente en formato MongoDB ObjectId
    """
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Paciente no encontrado"
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error interno: {status}"
    )

@app.get("/patient", 
         response_model=dict,
         summary="Buscar paciente por identificador")
async def get_patient_by_identifier(system: str, value: str):
    """
    Busca un paciente por su identificador (cédula, pasaporte, etc.)
    
    - **system**: Tipo de identificador (ej: 'http://cedula')
    - **value**: Valor del identificador
    """
    status, patient = GetPatientByIdentifier(system, value)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    raise HTTPException(status_code=500, detail=f"Error interno: {status}")

@app.post("/patient",
          response_model=dict,
          status_code=status.HTTP_201_CREATED,
          summary="Registrar nuevo paciente")
async def add_patient(request: Request):
    """
    Registra un nuevo paciente en el sistema con formato FHIR
    
    Requiere un objeto Patient válido según estándar FHIR
    """
    try:
        new_patient_dict = dict(await request.json())
        status, patient_id = WritePatient(new_patient_dict)
        
        if status == 'success':
            return {"_id": patient_id}
        elif 'errorValidating' in status:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Error de validación FHIR: {status}"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear paciente: {status}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en los datos recibidos: {str(e)}"
        )

@app.post("/patient/{patient_id}/medications",
          response_model=dict,
          status_code=status.HTTP_201_CREATED,
          summary="Registrar medicamento dispensado")
async def add_medication_dispense(
    patient_id: str,
    medication: MedicationDispenseCreate
):
    """
    Registra un medicamento dispensado en la historia clínica del paciente
    
    - **patient_id**: ID del paciente
    - **medication**: Datos del medicamento en formato MedicationDispense FHIR
    """
    # Convertir modelo Pydantic a dict y añadir timestamp
    medication_data = medication.dict()
    if not medication_data.get("timestamp"):
        medication_data["timestamp"] = datetime.now().isoformat()
    
    status, med_id = RegisterMedicationDispense(patient_id, medication_data)
    
    if status == 'success':
        return {
            "status": "success",
            "medication_id": med_id,
            "patient_id": patient_id
        }
    elif status == 'patientNotFound':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error al registrar medicamento: {status}"
    )

@app.get("/patient/{patient_id}/medications",
         response_model=List[Dict],
         summary="Obtener medicamentos del paciente")
async def get_patient_medications(patient_id: str):
    """
    Obtiene el historial completo de medicamentos dispensados a un paciente
    
    - **patient_id**: ID del paciente
    """
    status, medications = GetPatientMedications(patient_id)
    
    if status == 'success':
        return medications
    elif status == 'patientNotFound':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente no encontrado"
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error al obtener medicamentos: {status}"
    )

if __name__ == '__main__':
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True,
        workers=4
    )
