import requests
import numpy as np
import csv

from model.store import Store
from resources.conf import kakao

def csv_to_dict(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            result = {row[1]: row[0] for row in reader}
        return result
    
class Scrapping:
    def __init__(self):
        self.headers = {'Authorization' : f'KakaoAK {kakao["access_key"]}'}
        self.state = csv_to_dict('Gusto-Server-Store/resources/state_list.csv')
        self.city = csv_to_dict('Gusto-Server-Store/resources/city_list.csv')
        self.town = csv_to_dict('Gusto-Server-Store/resources/town_list.csv')
        
    # 위도 및 경도가 주어졌을 때 행정동 정보 가져와 code로 변경하기
    def getAddress(self, longitude, latitude):
        URL = kakao['address_url']
        params = {
            'x' : f'{longitude}',
            'y' : f'{latitude}'
        }
        
        data = requests.get(URL, params=params, headers=self.headers).json()
        h_data = data['documents'][1]
        
        
        address = {
            'state' : self.state.get(h_data['region_1depth_name']),
            'city' : self.city.get(h_data['region_2depth_name'].split()[0]),
            'town' : self.town.get(h_data['region_3depth_name'])
        }
        
        return address


    # 가게 정보가 list로 전달되는 documents 파싱하여 개별 store 정보로 변경하기
    def getStoreList(self, db_instance, documents):
        for store in documents:
            info = Store()
            
            # x, y 좌표로 행정동 코드 가져오기
            codes = self.getAddress(store['x'], store['y'])
            
            # 카테고리 결정하기 
            if(store['category_group_code'] == 'CE7'):
                info.category_string = '카페'
            else:
                # category 파싱하기 (AA > BB > CC 로 전달되는 것을 CC만 저장)
                
                categories = store['category_name'].split(' > ')
                category = categories[len(categories) - 1]
                
                info.category_string = category
                
                # 일부 "CC"로 표기된 것이 있어 해당 값 벗겨냄 
                if category.startswith('"'):
                    info.category_string = category[1:-1]
            
            # data 저장
            info.store_name = store['place_name']
            info.latitude = store['y']
            info.longitude = store['x']
            info.set_address(store['address_name'], store['road_address_name'], codes)
            info.contact = store['phone']
            
            # 해당 식당 정보가 이미 DB에 존재한다면 update, 존재하지 않는다면 create
            db_instance.update_store(info)

    # 데이터 검색하기
    def requestSearch(self, db_instance, start_x, start_y, end_x, end_y, width, height, category):
        URL = kakao['category_url']
        
        for x in np.arange(start_x, end_x, width):
            for y in np.arange(start_y, end_y, -height):
                params = {
                    'category_group_code' : category,
                    'rect' : f'{x},{y},{x + width},{y - height}'
                    }
                
                response = requests.get(URL, params=params, headers=self.headers)
                data = response.json()
                
                meta = data['meta']
                
                print(f'pagable: {meta["pageable_count"]}******')
                print(f'total: {meta["total_count"]}******')
            
                if(meta['total_count'] > meta['pageable_count']):
                    # readable한 수가 전체 수 보다 크면 공간을 4분할하여 정보를 얻어옴
                    self.requestSearch(db_instance, x, y, x + width/2, y - height/2, width/2, height/2, category)
                    self.requestSearch(db_instance, x + width/2, y, x + width, y - height/2, width/2, height/2, category)
                    self.requestSearch(db_instance, x, y - height/2, x + width/2, y - height, width/2, height/2, category)
                    self.requestSearch(db_instance, x + width/2, y - height/2, x + width, y - height, width/2, height/2, category)
                    
                else:
                    # page 1의 정보를 parsing
                    self.getStoreList(db_instance, data['documents']) # document 내 store List 접근
                    
                    if(meta['is_end'] == True):
                        continue
                    
                    # 이후 page 정보를 parsing
                    page = 2
                    while(True):
                        page_params = {
                            'category_group_code' : category,
                            'rect' : f'{x},{y},{x + width},{y - height}',
                            'page' : page
                            }
                        page_response = requests.get(URL, params=page_params, headers=self.headers).json()
                        
                        self.getStoreList(db_instance, page_response['documents'])
                        
                        if(page_response['meta']['is_end'] == True):
                            break
                        
                        page += 1