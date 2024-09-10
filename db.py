from resources.conf import ssh, db
from model.store import Store as store_dto
from entity.store import Store

from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os

class Database:
    def __init__(self):
        self.ssh_server =  SSHTunnelForwarder(
            (ssh['ssh_ip'], ssh['ssh_port']),
            ssh_username=ssh['ssh_username'],
            ssh_pkey=ssh['private_key'],
            remote_bind_address=(db['address'], db['port'])
        )
            
        self.ssh_server.start()
        
        print(self.ssh_server.is_active)
            
        self.engine = create_engine(
            'mysql+pymysql://{}:{}@{}:{}/{}'.format(db['id'], db['password'], "127.0.0.1", self.ssh_server.local_bind_port, db['schema'])
        )
        
        Sessionmaker = sessionmaker(self.engine)
        self.session = Sessionmaker()

    def close(self):
        self.session.close()
        self.ssh_server.stop()
    
    def update_store(self, store_dto):
        # 식당 정보는 식당 이름, x, y 값으로 검색함
        store_info = self.session.query(Store).filter(
            Store.store_name == store_dto.store_name,
            Store.longitude == store_dto.longitude,
            Store.latitude == store_dto.latitude
        ).first()
        
        # 해당 식당 정보가 이미 DB에 존재한다면 update, 존재하지 않는다면 create
        if store_info:
            store_info.category_string=store_dto.category_string
            store_info.contact=store_dto.contact
        else:
            new_store = Store(store_dto)
            self.session.add(new_store)
            
        self.session.commit()
        