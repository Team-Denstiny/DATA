import MongoDriver

mongo = MongoDriver.MongoDB()

def set_category():
    tmp_query = dict()
    tmp_query["치과교정과"] = ["임플란트"]
    tmp_query["통합치의학과"] = ["충치치료", "치아미백"]
    tmp_query["구강내과"] = ["사랑니발치", "잇몸치료", "치아미백"]
    tmp_query["구강악안면외과"] = ["임플란트", "사랑니발치"]
    tmp_query["소아치과"] = ["어린이"]
    tmp_query["영상치의학과"] = ["기타"]
    tmp_query["예방치과"] = ["스케일링"]
    tmp_query["치과보존과"] = ["충치치료", "라미네이트"]
    tmp_query["치과보철과"] = ["임플란트", "라미네이트"]
    tmp_query["치주과"] = ["잇몸치료", "스케일링"]
    tmp_query["치과"] = ["기타"]

    query_list = []
    for item in tmp_query:
        each_query = {
            'cate': item,
            'list': tmp_query[item]
        }
        query_list.append(each_query)

    mongo.insert(dbName="Hospital", tableName="category", queryList=query_list,
                 primaryKeySet=True, primaryKey='cate')

def get_category_each(name: str) -> list:
    ''' name에 해당하는 카테고리 쿼리 받아오기
    :param name:
    :return:
    '''
    query = {'cate': {'$eq': name}}
    object = mongo.read_last_one(dbname="Hospital", tablename="category", query=query)
    if object is None:
        return []
    return object['list']

def get_category(hospi_id) -> list:
    ''' name_list안의 세부 카테고리를 합쳐주는 함수
    :param hospi_id: 병원 id
    :return:
    '''

    obj = mongo.read_list_obj("Hospital", tablename="dynamicInfo", query={"id":hospi_id})
    name_list = obj["treat_cate"]
    sets = set()
    for item in name_list:
        cate_list = get_category_each(item)
        if not cate_list:
            continue
        sets.update(cate_list)
    if not sets:
        return []
    return list(sets)

def get_category_query(query: dict) -> list:
    name_list = query["treat_cate"]
    sets = set()
    for item in name_list:
        cate_list = get_category_each(item)
        if not cate_list:
            continue
        sets.update(cate_list)
    if not sets:
        return []
    return list(sets)



if __name__ == "__main__":
    print("Start..")
