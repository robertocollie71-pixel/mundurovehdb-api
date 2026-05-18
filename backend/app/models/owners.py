from sqlalchemy import Column, Integer, String, Text, Date
from sqlalchemy.orm import relationship
from backend.app.models.base import Base

class Owner(Base):
    __tablename__ = "owners"

    id = Column(Integer, primary_key=True, index=True)
    pesel_hash = Column(String(64), nullable=True, index=True)
    
    imie = Column(String(50), nullable=False)
    nazwisko = Column(String(50), nullable=False)
    
    # KLUCZ BIZNESOWY – numer telefonu jest nadrzędny do imienia i nazwiska
    nr_telefonu_enc = Column(
        Text, 
        nullable=False, 
        unique=True,      # jeden numer = jedna osoba
        index=True        # przyspiesza wyszukiwanie w panelu policyjnym i obywatelskim
    )
    
    data_urodzenia = Column(Date, nullable=True)
    access_level = Column(Integer, nullable=True, default=1)

    # Relacja z pojazdami
    vehicles = relationship("Vehicle", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Owner {self.imie} {self.nazwisko} | tel: {self.nr_telefonu_enc}>"
