class Store:
    def __init__(self):
        self.store_name = None
        self.category_string = None
        self.longitude = None
        self.latitude = None
        self.address = None
        self.old_address = None
        self.contact = None
        self.state_id = None
        self.town_id = None
        self.city_id = None
    
    def set_address(self, address, old_address, codes):
        self.address = address
        self.old_address = old_address
        self.state_id = codes['state']
        self.city_id = codes['city']
        self.town_id = codes['town']