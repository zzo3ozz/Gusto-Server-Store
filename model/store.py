class Store:
    def __init__(self):
        self.store_id
        self.store_name
        self.category_string
        self.longitude
        self.latitude
        self.address
        self.old_address
        self.contact
        self.state_id
        self.town_id
        self.city_id
        self.status
        self.created_at
        self.updated_at
    
    def set_address(self, address, old_address, codes):
        self.address = address
        self.old_address = old_address
        self.state_id = codes['state']
        self.city_id = codes['city']
        self.town_id = codes['town']