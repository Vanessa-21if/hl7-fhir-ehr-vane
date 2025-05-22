from fastapi import FastAPI, HTTPException, Request
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
from typing import List, Dict

app = FastAPI(
    title="Sistema de Salud - Historia Clínica Electrónica",
    description="API para gestión de pacientes y registro de medicamentos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hl7-patient-write-vanessa.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/patient/{patient_id}", response_model=dict)
async def get_patient_by_id(patient_id: str):
    status, patient = GetPatientById(patient_id)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.get("/patient", response_model=dict)
async def get_patient_by_identifier(system: str, value: str):
    status, patient = GetPatientByIdentifier(system, value)
    if status == 'success':
        return patient
    elif status == 'notFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Internal error. {status}")

@app.post("/patient", response_model=dict)
async def add_patient(request: Request):
    new_patient_dict = dict(await request.json())
    status, patient_id = WritePatient(new_patient_dict)
    if status == 'success':
        return {"_id": patient_id}
    else:
        raise HTTPException(status_code=500, detail=f"Validating error: {status}")

@app.post("/patient/{patient_id}/medications", response_model=dict)
async def add_medication_dispense(patient_id: str, request: Request):
    """
    Registra un medicamento dispensado en la historia clínica del paciente
    """
    medication_data = dict(await request.json())
    
    # Validación básica de datos requeridos
    if not medication_data.get("medication"):
        raise HTTPException(status_code=400, detail="Medication name is required")
    
    # Añadir timestamp si no viene en la petición
    if "timestamp" not in medication_data:
        medication_data["timestamp"] = datetime.now().isoformat()
    
    status, med_id = RegisterMedicationDispense(patient_id, medication_data)
    
    if status == 'success':
        return {"status": "success", "medication_id": med_id}
    elif status == 'patientNotFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Error registering medication: {status}")

@app.get("/patient/{patient_id}/medications", response_model=List[Dict])
async def get_patient_medications(patient_id: str):
    """
    Obtiene el historial de medicamentos dispensados a un paciente
    """
    status, medications = GetPatientMedications(patient_id)
    
    if status == 'success':
        return medications
    elif status == 'patientNotFound':
        raise HTTPException(status_code=404, detail="Patient not found")
    else:
        raise HTTPException(status_code=500, detail=f"Error retrieving medications: {status}")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
