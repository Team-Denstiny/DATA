from collections import deque

gu_dict = {
    "강서구" : ["구로구", "양천구", "마포구", "은평구"],
    "양천구" : ["강서구","마포구","영등포구","구로구","금천구"],
    "구로구" : ["양천구","강서구","영등포구","동작구","관악구","금천구"],
    "금천구" : ["구로구","양천구","영등포구","동작구","관악구"],
    "영등포구" : ["강서구","양천구","구로구","금천구","관악구","동작구","용산구","마포구"],
    "동작구" : ["영등포구","구로구","금천구","관악구","서초구","용산구","마포구"],
    "관악구" : ["구로구","금천구","영등포구","동작구","서초구"],
    "서초구": ["동작구","관악구","용산구","성동구","강남구"],
    "강남구" :["서초구","용산구","성동구","광진구","송파구"],
    "송파구" : ["강남구","성동구","광진구","강동구"],
    "강동구" : ["송파구","광진구","중랑구"],
    "광진구" : ["중랑구","동대문구","성동구","강남구","송파구","강동구"],
    "성동구" : ["중구","용산구","서초구","강남구","광진구","동대문구", "성북구","종로구"],
    "용산구" : ["서대문구","마포구","영등포구","동작구","서초구","강남구","성동구","중구"],
    "마포구" : ["강서구","양천구","영등포구","용산구","중구","서대문구","은평구"],
    "서대문구" : ["은평구","마포구","용산구","중구","종로구"],
    "은평구" : ["마포구","서대문구","종로구"],
    "종로구" : ["은평구","서대문구","중구","동대문구","성북구"],
    "중구" : ["종로구", "서대문구","마포구","용산구","성동구","동대문구","성북구"],
    "동대문구" : ["성북구","종로구","중구","성동구","광진구","중랑구","노원구"],
    "중랑구" : ["동대문구","성동구","광진구","노원구","강북구"],
    "성북구" : ["종로구","중구","성동구","동대문구","노원구","도봉구","강북구"],
    "강북구": ["종로구","성북구","도봉구","노원구","중랑구"],
    "도봉구" : ["강북구", "성북구","노원구"],
    "노원구" :["도봉구", "강북구","성북구","동대문구","중랑구"]
}

def search_dist(start, depth=2):
    visited = dict()
    for idx in gu_dict.keys():
        visited[idx] = False
    visited[start] = True

    queue = deque()
    queue.append((start, 0))
    ret_gu_list = [start]
    while queue:
        gu, dep = queue.popleft()
        for other_gu in gu_dict[gu]:
            if visited[other_gu] or depth <= dep:
                continue

            visited[other_gu] = True
            queue.append((other_gu, dep+1))
            ret_gu_list.append(other_gu)

    return ret_gu_list



if __name__ =="__main__":
    rets = search_dist(start="성북구", depth=1)
    print(rets)