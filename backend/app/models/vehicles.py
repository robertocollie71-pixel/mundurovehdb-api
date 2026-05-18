from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.models.base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    numer_rejestracyjny = Column(String, unique=True, nullable=False, index=True)   # <--- DODANE unique=True
    vin = Column(String, nullable=True)
    marka_model = Column(String, nullable=True)
    rok_produkcji = Column(Integer, nullable=True)
    data_waznosci_badania_technicznego = Column(Date, nullable=True)

    owner_id = Column(Integer, ForeignKey("owners.id"))
    owner = relationship("Owner", back_populates="vehicles")