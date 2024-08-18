import bs4
import requests
import urllib.parse
import pandas as pd
import os
import json
import MongoDriver
import time
import re
import datetime
from collections import deque
import set_category
from bson import ObjectId

mongo = MongoDriver.MongoDB()
excel_df = pd.DataFrame()
cookie = {'NNB': 'D7R7WEYBRTKGK'}
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Whale/3.27.254.15 Safari/537.36"}

def find_json_path(json_dict: dict, find_key, find_value=None):
    ''' Json Query 의 key: value의 구체적 경로를 찾아주는 함수
    :param json_dict:
    :param find_key:
    :param find_value:
    :return:
    '''

    queue_spool = deque()
    queue_spool.append((json_dict, ""))

    ## BFS 기반 Query 경로 찾아주는 로직
    while queue_spool:
        sub_dict, sub_path = queue_spool.popleft()
        for key, value in sub_dict.items():
            if isinstance(value, dict):
                queue_spool.append((value, f"{sub_path}[{key}]"))
            elif isinstance(value, list):
                for i, list_item in enumerate(value):
                    if isinstance(list_item, dict):
                        queue_spool.append((list_item, f"{sub_path}[{i}]"))

            if key == find_key and (not find_value or find_value == value):
                print(f"find! {sub_path}[{find_key}] -> {value}")

def hopital_id(id=19525089):
    ''' hospital_id 를 받으면 dictionary 로 변환 해주는 함수
    :param id:
    :return: dict (JSON 형태)
    '''
    global header, cookie, session
    url = f"https://pcmap.place.naver.com/hospital/{id}/home"

    response = requests.get(url, cookies=cookie, headers=header)
    response.encoding = 'utf-8'
    pas = bs4.BeautifulSoup(response.text, "html.parser").find_all('script')[2].text
           #replace("quot;", "").replace("&amp;", "")).replace("&lt;","").replace("&gt;","")

    #몇 번인지 찾아내기
    '''
    for i, item in enumerate(pas.split(';', maxsplit=9)):
        print(i)
        print(item)
        print("-----------------------------------------------")
    '''

    start_idx = pas.find("window.__APOLLO_STATE__")
    end_idx = pas.find("window.__PLACE_STATE__")
    json_query_str = pas[start_idx: end_idx].split('=', 1)[-1].strip()[:-1]
    try:
        return json.loads(json_query_str)
    except json.decoder.JSONDecodeError:
        print(json_query_str)
        print("-----------------------------")
        print(pas)
        return None

def find_dict_element_similar(json_dict: dict, key_list: list, exact_mode=False):
    ''' JSON 딕셔너리 원소 추출 함수
    ex) DICT[ROOT_QUERY][placeDetail({"input":{"deviceType":"mobile","id":"19525089","isNx":false}})][hospitalInfo][1]
    를 추출해야되면
    placeDetail(??) 를 추출 해야 되는데 해당 값은 가변 값 이니까.. 유사한 key 를 찾아서 해당 원소를 찾는다.
    다행히, placeDetail() 과 같은 함수는 2개이상 존재 하지 않기 때문 총총..

    :param json_dict: 딕셔너리
    :param key_list: 키 리스트
    :return: Object | None
    '''

    sub_query = json_dict

    for idx in key_list:
        find_flag = False

        # list 일 때
        if isinstance(sub_query, list) and isinstance(idx, int) and len(sub_query) > idx:
            sub_query = sub_query[idx]
            continue

        if not isinstance(sub_query, dict):
            return  None

        # dict 일 때
        for key in sub_query.keys():
                if (exact_mode and (idx == key)) or (not exact_mode and (idx in key)):
                    sub_query = sub_query[key]
                    find_flag = True
                    break

        if not find_flag:
            return None

    return sub_query

def get_naver_hospi_runtime(json_dict: dict, ret_query:dict):
    ''' 네이버 쿼리 기준 병원 시간 탐색
    :param json_dict:
    :param ret_query:
    :return:
    '''

    final_time_query = find_dict_element_similar(json_dict, ["ROOT_QUERY", "placeDetail", "newBusinessHours", 0, "businessHours"])
    ret_query['timeInfo'] = dict()

    if not final_time_query:
        day = ["월", "화", "수", "목", "금", "토", "일"]
        for d in day:
            sub_query = {
                "day": d,
                "work_time": ["00:00", "00:00"],
                "break_time": ["00:00", "00:00"],
                "description": ""
            }
            ret_query['timeInfo'][d] = sub_query

        return ret_query

    for day_info in final_time_query:
        ## {월, 화, 수, 목, 금, 토, 일} 형태로 한글자만 기록
        day = day_info['day'][:1]
        bussiness_time_obj = day_info['businessHours']
        breakhours_time_obj = day_info['breakHours']
        description = day_info['description']
        if not bussiness_time_obj:
            bussiness_time_obj = {'start': "00:00", 'end': "00:00"}
        if not breakhours_time_obj:
            breakhours_time_obj = {'start': "00:00", 'end': "00:00"}
        else:
            breakhours_time_obj = breakhours_time_obj[0]
        if not description:
            description = ""

        mongo_sub_query = {
            "day": day,
            "work_time": [bussiness_time_obj['start'], bussiness_time_obj['end']],
            "break_time": [breakhours_time_obj['start'], breakhours_time_obj['end']],
            "description": description
        }
        ret_query['timeInfo'][day] = mongo_sub_query
    return ret_query

def get_naver_hospi_category(json_dict: dict, ret_query:dict):
    cate = find_dict_element_similar(json_dict, ["ROOT_QUERY", "placeDetail", "hospitalInfo"])
    ret_query['treat_cate'] = []
    if not cate:
        return ret_query

    sub_list = list()
    sub_sort = cate["sortedSubjects"]
    for each in sub_sort:
        sub_list.append(each['name'])
    ret_query['treat_cate'] = sub_list
    return ret_query

def naver_dent_dict_parser_static(json_dict: dict):
    ''' 네이버 지도 딕셔너리에서 주요 element를 추출하는 함수. (바뀌지 않는 정보)
    :param json_dict:
    :return:
    '''

    ## print(json.dumps(json_dict, indent=2, ensure_ascii=False))
    ret_query = {}
    find_id = find_dict_element_similar(json_dict, ["PlaceDetailBase", "id"])
    ret_query['id'] = find_id
    ret_query["name"] = find_dict_element_similar(json_dict, [f'PlaceDetailBase:{find_id}', "name"], exact_mode=True)
    ret_query["addr"] = find_dict_element_similar(json_dict, ["PlaceDetailBase", "roadAddress"])
    dong_type = find_dict_element_similar(json_dict, ['PlaceDetailBase', "address"])
    ret_query["dong"] = None
    if dong_type:
        ret_query["dong"] = dong_type.split(" ")[0]

    telephone = find_dict_element_similar(json_dict, ["PlaceDetailBase", "phone"])

    if not telephone:
        telephone = find_dict_element_similar(json_dict, ["PlaceDetailBase", "virtualPhone"])
    ret_query["tele"] = telephone
    ret_query["img"] = find_dict_element_similar(json_dict,
                                                 ['ROOT_QUERY', "placeDetail", "images", "images", 0, "origin"])
    coord = find_dict_element_similar(json_dict, ['PlaceDetailBase', "coordinate"])
    if coord:
        ret_query["lon"] = float(coord['x'])
        ret_query["lat"] = float(coord['y'])

    ret_query['subway_info'] = ''
    ret_query['subway_name'] = ''
    ret_query['dist'] = 0
    trans = find_dict_element_similar(json_dict, ['ROOT_QUERY', 'placeDetail', "subwayStations"])
    #print(json.dumps(obj=json_dict, indent=2, ensure_ascii=False))
    transSimilar = find_dict_element_similar(json_dict, ['SubwayStationInfo:'])
    if trans:
        trans = trans[0]
        ret_query['subway_info'] = trans['no']

    if transSimilar:
        ret_query['subway_name'] = transSimilar['name'] + '역'
        ret_query['dist'] = int(transSimilar['walkingDistance'])
    elif trans:
        ret_query['subway_name'] = trans['station']['name'] + '역'
        ret_query['dist'] = int(trans['station']['walkingDistance'])
    print(ret_query)
    return ret_query

def naver_dent_dict_parser_dynamic(json_dict: dict):
    ''' 네이버 지도 딕셔너리에서 주요 element를 추출하는 함수. (자주 바뀌는 정보) => Insert가 아닌 update 를 해줘야되는 table 임..
    :param json_dict:
    :return:
    '''

    ret_query = {}

    ##### 가변 데이터 ?
    find_id = find_dict_element_similar(json_dict, ["PlaceDetailBase", "id"])
    ret_query['id'] = find_id
    ret_query["name"] = find_dict_element_similar(json_dict, [f'PlaceDetailBase:{find_id}', "name"], exact_mode=True)
    ret_query['score'] = find_dict_element_similar(json_dict, ["PlaceDetailBase", "visitorReviewsScore"])
    ret_query['review_cnt'] = find_dict_element_similar(json_dict, ["PlaceDetailBase", "visitorReviewsTotal"])
    ret_query = get_naver_hospi_runtime(json_dict, ret_query)
    ret_query = get_naver_hospi_category(json_dict, ret_query)
    ret_query['review'] = []

    ret_query["treat_cate_easy"] = set_category.get_category_query(query=ret_query)

    return ret_query

def crawl_parser(name, lat, long):
    encoding_name = urllib.parse.quote(name)
    global header, cookie
    url = f"https://map.naver.com/p/api/search/allSearch?query={encoding_name}&type=all&searchCoord={long}%3B{lat}&boundary="
    print(url)
    response = requests.get(url, cookies=cookie, headers=header)
    if response.status_code == 200:
        try:
            data = response.json().get("result").get("place").get("list")
        except AttributeError as e:
            print(f"{name} is not existed ---> ")
            return

        hospital_list = []
        for item in data:
            obj_name = item.get("name")
            id = item.get("id")
            road_addr = item.get("roadAddress")
            abbr_addr = item.get("abbrAddress")
            tel_name = item.get("tel")
            print(f"id:{id} 병원명: {obj_name}, 주소={road_addr}, 전화번호={tel_name}")
            if "서울" in road_addr:
                query = {'id': id, 'name': obj_name, 'addr': road_addr}
                mongo.insert_hospital_code(query)

            print("-------------------------------------")
    else:
        print(f"error : Parsing {response.text}")
    time.sleep(1)
    #print(BeautifulSoup(response.text, "html.parser"))

def getExcel(url="dentist.xlsx"):
    ''' 엑셀 파일 읽기 '''
    global excel_df
    f_path = os.path.join(os.getcwd(), url)
    excel_df = pd.read_excel(f_path)

def procExcel():
    if len (excel_df) == 0:
        getExcel()
    for row in excel_df.itertuples(index=False, name="Pandas"):
        print(f"병원명={row.병원명}, 주소={row.주소}")
        find_data = mongo.read_hospital_code(row.병원명)
        if find_data:
            print(f"{row.병원명} 코드 존재.. continue")
            continue
        crawl_parser(row.병원명, lat=37, long=127)


def naverInfo_updater():
    all_ids = mongo.read_all_hospital_code()
    for each in all_ids:
        exist_check = mongo.read_staticInfo_code(each['id'])
        print(f"{each['name']} update start ...")
        ret_dict = hopital_id(each['id']) # Query 업데이트 시작
        if exist_check:
            print(f"{each['name']} 데이터 이미 존재 continue...")
        else:
            ret_static_query = naver_dent_dict_parser_static(ret_dict)
            mongo.insert_staticInfo_code(ret_static_query)  # 바꿔야함.
        if not ret_dict:
            continue

        ret_dynamic_query = naver_dent_dict_parser_dynamic(ret_dict)
        mongo.insert_dynamicInfo_code(ret_dynamic_query)

        time.sleep(0.5)

#####TEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMP####
def make_review_block():
    data = mongo.read_all_hospital_code()
    queries = []
    for each in data:
        make_query = {
            "id": each['id'],
            "name": each["name"],
            "review": []
        }
        queries.append(make_query)
        print(make_query)
    mongo.insert(dbName="Hospital", tableName="review", queryList=queries, primaryKey='id', primaryKeySet=True)

#####TEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMPTEMP####

if __name__ == "__main__":
    #procExcel()

    #dicts = hopital_id(38747300)
    #ret_query = naver_dent_dict_parser_static(dicts)
    #print(ret_query)
    #print(ret_query)
    #crawl_parser("새서울치과", 37, 127)
    naverInfo_updater()


    ## 월요일 후무 쿼리 검색 시 --> {"timeInfo.월.description": "휴무"}

    ## Json Finder

    def temp():

        fname = "exam_json.txt"
        json_dict = None
        with open(fname, "rt", encoding="UTF8") as f:
            json_dict = json.load(f)

        print(json.dumps(obj=json_dict, indent=2, ensure_ascii=False))

        find_json_path(json_dict, find_key="SubwayStationInfo")

        trans = find_dict_element_similar(json_dict, ['ROOT_QUERY', 'placeDetail', "subwayStations"])
        find_json_path(json_dict, find_key="SubwayStationInfo:1516")

        if trans:
            trans = trans[0]
            subway_info = trans['name'] + '선'
            subway_name = trans['station']['name'] + '역'
            dist = int(trans['station']['walkingDistance'])

    #temp()
    def check_day_off():
        each_test = mongo.read_each_day_off_hospital("월")
        for each in each_test:
            print(f"{each['name']}, {[each['timeInfo'][day]['description'] for day in ['월', '화', '수', '목', '금', '토', '일']]}")
    def check_day_off_all():
        each_test = mongo.read_all_day_off_hospital()
        for each in each_test:
            print(
                f"{each['name']}, {[each['timeInfo'][day]['description'] for day in ['월', '화', '수', '목', '금', '토', '일']]}")



    def make_comment(comment: "", hospiId="", score=1):
        review_query = {
            "nickName": "hihihihi",
            "hospitalId": hospiId,
            "date": datetime.datetime.utcnow(),
            "review_score": score,
            "user_id": 1,
            "content":comment
        }
        mongo.insert(dbName="Hospital", tableName="review", queryList=[review_query])
        id1 = mongo.read_dynamicInfo_code(hospiId)
        that_query = mongo.read_last_one(dbname="Hospital", tablename="review", query={'hospitalId': hospiId})

        if id1:
            id1["review"] = [that_query['_id']]
            mongo.replace_one(dbName="Hospital", tableName="dynamicInfo", origin_query={"id":hospiId}, query=id1)


    make_comment(comment="봄은 무슨 봄입니까 봄봄입니까?", hospiId="1893859791", score=1)
    make_comment(comment="좋지 못하네요 나갔으면 좋곘습니다", hospiId="19525089", score=2)
    make_comment(comment="병원이 강남 편안한 치과인데 전혀 편안하지 않습니다 너무 불안합니다. 선생님이 자꾸 정치성향을 드러냅니다..", hospiId="1016812270", score=3)
    make_comment(comment="아주 좋습니다 좋아요 너무 좋네요 정말 좋아요 아 좋습니다 좋아요", hospiId="1893859791", score=4)
