from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^(?:\+?48)?\d{9}$")

class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^(?:\+?48)?\d{9}$")
    code: str = Field(..., min_length=6, max_length=6)

class CitizenVehicleRequest(BaseModel):
    phone_number: str = Field(..., pattern=r"^(?:\+?48)?\d{9}$")
    registration_numbers: List[str] = Field(..., min_items=1, max_items=10)

class CitizenVehicleResponse(BaseModel):
    numer_rejestracyjny: str
    vin: Optional[str] = None
    marka_model: str
    rok_produkcji: int
    data_waznosci_badania: Optional[date] = None
    status: str = "OK"

class CitizenResponse(BaseModel):
    success: bool
    message: str
    vehicles: List[CitizenVehicleResponse] = []