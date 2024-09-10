from sqlalchemy import Column, Integer, String, BigInteger, Float, Enum, DateTime
from base import Base
from model.store import Store as store_dto
import enum
import datetime


class StatusEnum(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    CLOSED = "CLOSED"

class Store(Base):
    __tablename__='store'
    
    store_id = Column(BigInteger, primary_key=True, autoincrement=True)
    store_name = Column(String(30))
    category_string = Column(String(20))
    longitude = Column(Float(17, 14))
    latitude = Column(Float(17, 15))
    address = Column(String(60), nullable=False)
    old_address = Column(String(60))
    contact = Column(String(20))
    state_id = Column(BigInteger, nullable=False)
    city_id = Column(BigInteger, nullable=False)
    town_id = Column(BigInteger, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False, default=StatusEnum.ACTIVE)
    created_at = Column(DateTime(6), nullable=False, default=datetime.datetime.now(datetime.UTC))
    updated_at = Column(DateTime(6), nullable=False,default=datetime.datetime.now(datetime.UTC), onupdate=datetime.datetime.now(datetime.UTC))
    img1 = Column(String(255))
    img2 = Column(String(255))
    img3 = Column(String(255))
    img4 = Column(String(255))
    
    def __repr__(self):
        return f"<Store(store_id={self.store_id}, store_name={self.store_name}, status={self.status})>"
    
    def __init__(self, store_dto):
        self.store_name = store_dto.store_name
        self.category_string = store_dto.category_string
        self.longitude = store_dto.longitude
        self.latitude = store_dto.latitude
        self.address = store_dto.address
        self.old_address = store_dto.old_address
        self.contact = store_dto.contact
        self.state_id = store_dto.state_id
        self.town_id = store_dto.town_id
        self.city_id = store_dto.city_id