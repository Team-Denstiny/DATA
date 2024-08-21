import math
import MongoDriver
import main
import requests
import bs4
import json
import NaverGraphQL

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






def getReview(id: str) -> dict:
    hospi_name_obj = mongo.read_hospital_code(id)
    if not hospi_name_obj:
        return

    hospi_name = hospi_name_obj["name"]

    url = f"https://pcmap.place.naver.com/hospital/{id}/review/visitor?type=list"
    print(f"{url}")
    cookie = main.cookie
    header = main.header
    response = requests.get(url, cookies=cookie, headers=header)

    response.encoding = 'utf-8'
    element = bs4.BeautifulSoup(response.text, "html.parser")

    apollo = getScript(bs4Element=element)
    # main.find_json_path(json_dict=apollo, find_key="total", find_value=204) ##find 해보기
    find_total_reviews = main.find_dict_element_similar(json_dict=apollo, key_list=["ROOT_QUERY", "visitorReviews", "total"])
    if not find_total_reviews:
        return

    find_total_reviews = int(find_total_reviews)
    page_cnt = math.ceil(find_total_reviews / 50)

    ret_query_list = []
    for page_num in range(1, page_cnt+1):
        #print(f"page_num = {page_num}")
        res = getReviews50(hospi_id=id, page_id=page_num)
        json_dict = json.loads(res.text)
        review_query_list = processReviewJson(review_json=json_dict)
        ret_query_list.extend(review_query_list)

    db_query = {
        "id": id,
        "name": hospi_name,
        "reviews": ret_query_list
    }
    mongo.insert(dbName="Reviews", tableName="reviews", primaryKey="id", primaryKeySet=True, queryList=[db_query])

def processReviewJson(review_json: json):
    #print(json.dumps(review_json, indent=2, ensure_ascii=False))
    element = main.find_dict_element_similar(review_json, [0, "data", "visitorReviews", "items"])
    query_list = []
    for each in element:
        query = dict()
        query["id"] = each['id']
        query["review"] = each['body']
        keyword_list = each["visitKeywords"]
        query["reserve"] = ""
        query["waitTime"] = ""
        for each_key in keyword_list:
            if each_key["code"] == "v_with_reservation":
                query["reserve"] = each_key["keywords"][0]
            elif each_key["code"] == "v_more_than_1hour":
                query["waitTime"] = each_key["keywords"][0]
        query_list.append(query)

    return query_list


def getReviews50(hospi_id:str, page_id=1):
    payload = [
        {
            "operationName": "getVisitorReviews",
            "variables": {
                "input":
                     {"businessId": hospi_id,
                      "businessType": "hospital",
                      "item": "0",
                      "bookingBusinessId": None,
                      "page": page_id,
                      "size": 50,
                      "isPhotoUsed": False,
                      "includeContent": True,
                      "getUserStats": True,
                      "includeReceiptPhotos": True,
                      "cidList": ["223175", "223176", "223187", "223256", "223263"],
                      "getReactions": True,
                      "getTrailer": True
                      },
                 "id": hospi_id
            },
            "query": NaverGraphQL.graph_query
        }
    ]

    request_header = {
        'Content-Type': 'application/json',
        "User-Agent": main.header["User-Agent"]
    }

    url = "https://pcmap-api.place.naver.com/graphql"
    res = requests.post(
        url=url,
        headers=request_header,
        cookies=main.cookie,
        json=payload
    )

    if res.status_code == 200:
        return res
    else:
        return None


def updateAllReviews():
    all_code = mongo.read_all_hospital_code()
    for code in all_code:
        getReview(code["id"])

if __name__ == "__main__":
    updateAllReviews()
