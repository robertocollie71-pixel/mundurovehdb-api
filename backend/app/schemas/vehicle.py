from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class OwnerBase(BaseModel):
    """Główny model właściciela – numer telefonu jest kluczowy"""
    imie: str
    nazwisko: str
    phone: str          # <--- wymagane pole, bez wartości domyślnej

    model_config = ConfigDict(from_attributes=True)


class VehicleResponse(BaseModel):
    numer_rejestracyjny: str
    vin: Optional[str] = None
    marka_model: str
    rok_produkcji: int
    data_waznosci_badania: Optional[date] = None
    wlasciciel: Optional[OwnerBase] = None

    model_config = ConfigDict(from_attributes=True)
