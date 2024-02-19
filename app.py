import requests
import numpy as np
import csv

from config import kakao

headers = {'Authorization' : f'KakaoAK {kakao["access_key"]}'}

# 위도 및 경도가 주어졌을 때 행정동 정보 가져오기
def getAddress(longitude, latitude):
    URL = kakao['address_url']
    params = {
        'x' : f'{longitude}',
        'y' : f'{latitude}'
    }
    
    data = requests.get(URL, params=params, headers=headers).json()
    h_data = data['documents'][1]
    
    
    address = {
        'state' : h_data['region_1depth_name'],
        'city' : h_data['region_2depth_name'].split()[0],
        'town' : h_data['region_3depth_name']
    }
    
    return address


# 가게 정보가 list로 전달되는 documents 파싱하여 dict list 반환하기
def getStoreList(documents):
    infos = list()
    for store in documents:
        address = getAddress(store['x'], store['y'])
        
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


def requestSearch(start_x, start_y, end_x, end_y, width, height, category):
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
                result.extend(requestSearch(x, y, x + width/2, y - height/2, width/2, height/2, category))
                result.extend(requestSearch(x + width/2, y, x + width, y - height/2, width/2, height/2, category))
                result.extend(requestSearch(x, y - height/2, x + width/2, y - height, width/2, height/2, category))
                result.extend(requestSearch(x + width/2, y - height/2, x + width, y - height, width/2, height/2, category))
                
            else:
                # page 1의 정보를 parsing
                result.extend(getStoreList(data['documents']))
                
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
                    page_response = requests.get(URL, params=page_params, headers=headers).json()
                    result.extend(getStoreList(page_response['documents']))
                    
                    if(page_response['meta']['is_end'] == True):
                        break
                    
                    page += 1
    return result

# 시작 지점에 맞게 변경 
start_x = 126.8777806 # longitude
start_y = 37.5231736 # latitude

# 종료 지점에 맞게 변경
end_x = 126.9045751 # longtidue
end_y = 37.5088873 # latitude

# 경도(width), 위도(height) 변량
width = 0.00175#0.0015
height = 0.00175#0.0015

result = requestSearch(start_x, start_y, end_x, end_y, width, height, 'FD6')
result.extend(requestSearch(start_x, start_y, end_x, end_y, width, height, 'CE7'))

## csv로 저장
with open("result.csv", 'w', encoding="UTF-8") as file:
    writer = csv.writer(file)
    writer.writerows(result)





    
    