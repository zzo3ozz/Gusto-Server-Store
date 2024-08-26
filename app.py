import scrapping

if __name__ == '__main__':
    # 시작 지점에 맞게 변경 
    start_x = 126.8777806 # longitude
    start_y = 37.5231736 # latitude

    # 종료 지점에 맞게 변경
    end_x = 126.9045751 # longtidue
    end_y = 37.5088873 # latitude

    # 경도(width), 위도(height) 변량
    width = 0.00175#0.0015
    height = 0.00175#0.0015

    # 음식점 검색
    scrapping.requestSearch(start_x, start_y, end_x, end_y, width, height, 'FD6')

    # 카페 검색 
    scrapping.requestSearch(start_x, start_y, end_x, end_y, width, height, 'CE7')

        
        