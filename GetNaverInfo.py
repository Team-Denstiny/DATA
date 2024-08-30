import math
import MongoDriver
import main
import requests
import bs4
import json
import time


mongo = MongoDriver.MongoDB()
def getOnlyReviewGroups(json_obj: json) -> list:
    find_review_wrapper = main.find_dict_element_similar(json_obj, ["ROOT_QUERY", "visitorReviews", "items"])
    ret_list = []
    for each in find_review_wrapper:
        each_strs = each['__ref']
        review_only_key = each_strs.split(":")[1]
        ret_list.append(review_only_key)

    return ret_list

def getScript(bs4Element: bs4.BeautifulSoup, value="__APOLLO_STATE__"):
    ''' Naver script 중에 value를 찾아서 리턴
    Sccript 종류 = [__APOLLO_STATE__, __PLACE_STATE__, __LOCATION_STATE__, __PROFILE_STATE__]
    :param bs4Element:
    :param value:
    :return:
    '''
    if not bs4Element:
        return None

    script = bs4Element.find_all("script")
    get_element = None
    for each in script:
        each = each.text.strip()
        if "var naver" in each:
            get_element = each
            break

    element_list = get_element.split("window.")
    json_str = None
    for each in element_list:
        if value in each:
            try:
                json_str = each.split("=", maxsplit=1)[-1].strip()[:-1]
            except Exception:
                return None
            break

    if not json_str:
        return None

    json_obj = json.loads(json_str)
    return json_obj

def getInfo(id: str) -> dict:
    hospi_name_obj = mongo.read_hospital_code(id)
    if not hospi_name_obj:
        return

    hospi_name = hospi_name_obj["name"]
    url = f"https://pcmap.place.naver.com/hospital/{id}/information"
    print(f"{url}")
    cookie = main.cookie
    header = main.header
    response = requests.get(url, cookies=cookie, headers=header)

    response.encoding = 'utf-8'
    element = bs4.BeautifulSoup(response.text, "html.parser")

    apollo = getScript(bs4Element=element)
    intro = main.find_dict_element_similar(json_dict=apollo, key_list=["ROOT_QUERY", "placeDetail", "description"])
    #main.find_json_path(apollo, "description")
    keywords = element.find_all("span", "RLvZP")
    services = element.find_all("div", "owG4q")
    carInfo = element.find("div", "qbROU")
    cashInfo = element.find_all("div", "OnLFW")

    query = {}
    if intro:
        query["intro"] = intro

    if keywords:
        query["keyword"] = [item.text for item in keywords]

    if services:
        query["service"] = [item.text for item in services]

    if carInfo:
        park_check = carInfo.find("div", "TZ6eS")
        query["parking"] = park_check.text

    if cashInfo:
        query["cash"] = [item.text for item in cashInfo]

    print(query)
    '''
    db_query = {
        "id": id,
        "name": hospi_name,
        "reviews": ret_query_list
    }
    #mongo.insert(dbName="Reviews", tableName="reviews", primaryKey="id", primaryKeySet=True, queryList=[db_query])
    '''

def updateAllReviews():
    all_code = mongo.read_all_hospital_code()
    for code in all_code:
        getInfo(code["id"])
        time.sleep(0.5)

if __name__ == "__main__":
    getInfo("1016812270")