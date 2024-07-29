import bs4
import requests
import urllib.parse
import pandas as pd
import os
import json
import MongoDriver
import time
import re


mongo = MongoDriver.MongoDB()
excel_df = pd.DataFrame()
cookie = {'NNB': 'D7R7WEYBRTKGK'}
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Whale/3.27.254.15 Safari/537.36"}

def hopital_id(id=19525089):
    global header, cookie, session
    url = f"https://pcmap.place.naver.com/hospital/{id}/home"

    response = requests.get(url, cookies=cookie, headers=header)
    response.encoding = 'utf-8'
    pas = (bs4.BeautifulSoup(response.text, "html.parser").find_all('script')[2].text.
           replace("quot;", "").replace("&amp;", "")).replace("&lt;","").replace("&gt;","")


    #몇 번인지 찾아내기
    '''
    for i, item in enumerate(pas.split(';', maxsplit=9)):
        print(i)
        print(item)
        print("-----------------------------------------------")
    '''

    json_query_str = pas.split(';')[8].strip().split('=', 1)[-1]

    try:
        json_dict = json.loads(json_query_str)
    except json.decoder.JSONDecodeError:
        print(json_query_str)
        print("-----------------------------")
        print(pas)
        return None
    json_keys = list(json_dict.keys())

    hospi_info_dict_key = ""
    for item in json_keys:
        if "PlaceDetailBase" in item:
            hospi_info_dict_key = item
            break
    hospi_info_dict = json_dict[hospi_info_dict_key]
    sub1_dict = json_dict["ROOT_QUERY"]
    ret_query = {}
    ret_query['id'] = id
    ret_query["name"] = hospi_info_dict["name"]
    ret_query["road_address"] = hospi_info_dict["roadAddress"]
    ret_query["telephone"] = hospi_info_dict['phone']
    ret_query['visitor_score'] = hospi_info_dict['visitorReviewsScore']

    sub1_key = list(sub1_dict.keys())[3]
    sub2_dict = sub1_dict[sub1_key]
    sub2_key = list(sub2_dict.keys())[19]
    try:
        sub3_dict = sub2_dict[sub2_key][0]
    except IndexError:
        return ret_query

    final_time_query = sub3_dict["businessHours"]
    ret_query['timeInfo'] = dict()
    for day_info in final_time_query:
        day = day_info['day']
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

    time.sleep(0.8)
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
        exist_check = mongo.read_naverInfo_code(each['id'])
        if exist_check:
            print(f"{each['name']} 데이터 이미 존재 continue...")
            continue
        print(f"{each['name']} update start ...")
        ret_query = hopital_id(each['id']) # Query 업데이트 시작
        if not ret_query:
            continue
        mongo.insert_naverInfo_code(ret_query)

if __name__ == "__main__":
    #procExcel()
    #hopital_id(19525089)
    #crawl_parser("임플란피아치과의원", 37, 127)
    naverInfo_updater()
