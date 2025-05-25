from fastapi import FastAPI, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from app.controlador.PatientCrud import (
    WritePatient,
    RegisterMedicationDispense,
    GetPatientById,
    GetPatientMedications
)

app = FastAPI(
    title="API de Dispensación de Medicamentos",
    description="API para gestión de dispensación de medicamentos en formato FHIR",
    version="1.0.0",
    docs_url="/docs"
)

@app.api_route("/", methods=["GET", "HEAD"])  # Soporta GET y HEAD
def root():
    return {
        "status": "API funcionando",
        "routes": ["/docs", "/patient", "/patient/{id}/medications"]
    }


# CORS para permitir acceso desde frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hl7-fhir-ehr-vane.onrender.com", "https://hl7-patient-write-vanessa.onrender.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)



class PatientData(BaseModel):
    document: str

class MedicationData(BaseModel):
    nameMedicine: str
    presentation: str
    dose: str
    amount: int
    disgnosis: str
    recipeDate: str
    institution: str
    observations: str

class DispensationRequest(BaseModel):
    patient: PatientData
    medication: MedicationData
    
class DispenseInput(BaseModel):
    patient_id: str
    medication_name: str
    quantity: float
    days_supply: float
    dosage: str

# ========== NUEVO ENDPOINT UNIFICADO ==========

@app.post("/medications", summary="Registrar paciente + medicamento")
async def register_dispensation(payload: DispensationRequest):
    """
    Registra un paciente junto con la información del medicamento dispensado.
    """

    # 1. Guardar paciente
    patient_payload = {
        "document": payload.patient.document
    }
    status_p, patient_id = WritePatient(patient_payload)

    if status_p != "success":
        raise HTTPException(status_code=422, detail="Error registrando paciente")

    # 2. Guardar medicamento
    medication_payload = payload.medication.dict()
    print("medication_payload:", medication_payload)
    status_m, medication_id = RegisterMedicationDispense(patient_id, medication_payload)

    if status_m != "success":
        raise HTTPException(status_code=500, detail="Error registrando medicamento")

    return {
        "status": "success",
        "patient_id": patient_id,
        "medication_id": medication_id
    }
