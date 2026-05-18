from pydantic import BaseModel
from typing import Optional

class PhoneRequest(BaseModel):
    phone: str
    imie: str
    nazwisko: str

class VehicleRequest(BaseModel):
    numer_rejestracyjny: str
    phone: str
