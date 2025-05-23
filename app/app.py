from fastapi import FastAPI, HTTPException, status
import uvicorn
from app.controlador.PatientCrud import (
    GetPatientById,
    WritePatient,
    RegisterMedicationDispense,
    GetPatientMedications
)
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
from pydantic import BaseModel

app = FastAPI(
    title="API de Dispensación de Medicamentos",
    description="API para gestión de dispensación de medicamentos en formato FHIR",
    version="1.0.0",
    docs_url="/docs"
)

# Configuración CORS básica
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hl7-fhir-ehr-vane.onrender.com","https://hl7-patient-write-vanessa.onrender.com"],  #solo estos dominios
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Modelo simplificado para dispensación de medicamentos
class MedicationDispenseCreate(BaseModel):
    medicationName: str
    quantity: float
    daysSupply: float
    dosage: str

@app.get("/patient/{patient_id}", 
         summary="Obtener información básica de paciente",
         responses={
             404: {"description": "Paciente no encontrado"},
             500: {"description": "Error interno del servidor"}
         })
async def get_patient_by_id(patient_id: str):
    """
    Obtiene información básica de un paciente necesaria para dispensación
    
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
        detail="Error al recuperar paciente"
    )

@app.post("/patient",
          status_code=status.HTTP_201_CREATED,
          summary="Registrar nuevo paciente mínimo")
async def add_patient(patient_data: dict):
    """
    Registra un nuevo paciente con datos mínimos para dispensación
    
    Requiere:
    - name (given, family)
    - identifier (system, value)
    """
    status, patient_id = WritePatient(patient_data)
    
    if status == 'success':
        return {"patient_id": patient_id}
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Datos de paciente inválidos"
    )

@app.post("/patient/{patient_id}/medications",
          status_code=status.HTTP_201_CREATED,
          summary="Registrar medicamento dispensado")
async def add_medication_dispense(
    patient_id: str,
    medication: MedicationDispenseCreate
):
    """
    Registra una dispensación de medicamento con datos esenciales
    
    - **patient_id**: ID del paciente
    - **medicationName**: Nombre del medicamento
    - **quantity**: Cantidad dispensada
    - **daysSupply**: Días de tratamiento
    - **dosage**: Instrucciones de dosificación
    """
    medication_data = medication.dict()
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
        detail="Error al registrar medicamento"
    )

@app.get("/patient/{patient_id}/medications",
         summary="Obtener historial de dispensaciones")
async def get_patient_medications(patient_id: str):
    """
    Obtiene el historial de medicamentos dispensados a un paciente
    
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
        detail="Error al obtener medicamentos"
    )

if __name__ == '__main__':
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
    
