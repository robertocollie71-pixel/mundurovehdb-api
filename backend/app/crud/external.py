from sqlalchemy.orm import Session
from backend.app.models.owners import Owner
from backend.app.models.vehicles import Vehicle
from sqlalchemy.exc import IntegrityError

def get_or_create_owner_by_phone(db: Session, phone: str, imie: str, nazwisko: str):
    """Tworzy lub aktualizuje właściciela po numerze telefonu"""
    owner = db.query(Owner).filter(Owner.nr_telefonu_enc == phone).first()
    
    if owner:
        owner.imie = imie
        owner.nazwisko = nazwisko
        return owner
    
    owner = Owner(
        pesel_hash=f"hash_{phone}",
        imie=imie,
        nazwisko=nazwisko,
        nr_telefonu_enc=phone,
        access_level=1
    )
    db.add(owner)
    return owner

def add_vehicle_to_owner(db: Session, numer_rejestracyjny: str, phone: str):
    """Dodaje pojazd do właściciela (po telefonie)"""
    owner = db.query(Owner).filter(Owner.nr_telefonu_enc == phone).first()
    if not owner:
        raise ValueError("Nie znaleziono właściciela o podanym numerze telefonu")
    
    vehicle = Vehicle(
        numer_rejestracyjny=numer_rejestracyjny.upper(),
        owner_id=owner.id,
        marka_model="[dane z CEPiK]",
        rok_produkcji=2025,
        data_waznosci_badania_technicznego=None
    )
    db.add(vehicle)
    return vehicle

def get_all_citizens(db: Session):
    """Zwraca listę obywateli dla WordPress (format zgodny z frontendem)"""
    owners = db.query(Owner).all()
    result = []
    for owner in owners:
        vehicles = [v.numer_rejestracyjny for v in owner.vehicles]
        result.append({
            "phone": owner.nr_telefonu_enc,
            "imie": owner.imie,
            "nazwisko": owner.nazwisko,
            "vehicles": vehicles
        })
    return result
