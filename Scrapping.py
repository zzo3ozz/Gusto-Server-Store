import requests
import numpy as np
import csv

from config import kakao

def csv_to_dict(file_path):
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            result = [{row[1]: row[0]} for row in reader]
        return result
    
class Scrapping:
    def __init__(self):
        self.headers = {'Authorization' : f'KakaoAK {kakao["access_key"]}'}
        self.state = csv_to_dict('resources/state_list.csv')
        self.city = csv_to_dict('resources/city_list.csv')
        self.town = csv_to_dict('resources/town_list.csv')
        
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


    # 가게 정보가 list로 전달되는 documents 파싱하여 dict list 반환하기
    def getStoreList(self, documents):
        infos = list()
        for store in documents:
            address = self.getAddress(store['x'], store['y'])
            
            if(store['category_group_code'] == 'CE7'):
                category = '카페'
            else:
                categories = store['category_name'].split(' > ')
                category = categories[len(categories) - 1]
                if category.startswith('"'):
                    category = category[1:-1]
            
            info = [
                store['place_name'],
                ## category 파싱하기 (AA > BB > CC 로 전달되는 것을 CC만 저장)
                category,
                store['x'],
                store['y'],
                store['road_address_name'],
                store['address_name'],
                store['phone'],
                address['state'],
                address['city'],
                address['town']
            ]
            
            infos.append(info)
        
        return infos


    # 데이터 검색하기
    def requestSearch(self, start_x, start_y, end_x, end_y, width, height, category):
        URL = kakao['category_url']
        result = list()
        
        for x in np.arange(start_x, end_x, width):
            for y in np.arange(start_y, end_y, -height):
                params = {
                    'category_group_code' : category,
                    'rect' : f'{x},{y},{x + width},{y - height}'
                    }
                
                response = requests.get(URL, params=params, headers=headers)
                data = response.json()
                
                meta = data['meta']
                
                print(f'pagable: {meta["pageable_count"]}******')
                print(f'total: {meta["total_count"]}******')
            
                if(meta['total_count'] > meta['pageable_count']):
                    # readable한 수가 전체 수 보다 크면 공간을 4분할하여 정보를 얻어옴
                    result.extend(self.requestSearch(x, y, x + width/2, y - height/2, width/2, height/2, category))
                    result.extend(self.requestSearch(x + width/2, y, x + width, y - height/2, width/2, height/2, category))
                    result.extend(self.requestSearch(x, y - height/2, x + width/2, y - height, width/2, height/2, category))
                    result.extend(self.requestSearch(x + width/2, y - height/2, x + width, y - height, width/2, height/2, category))
                    
                else:
                    # page 1의 정보를 parsing
                    result.extend(self.getStoreList(data['documents']))
                    
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
                        result.extend(self.getStoreList(page_response['documents']))
                        
                        if(page_response['meta']['is_end'] == True):
                            break
                        
                        page += 1
        return result