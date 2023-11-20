import requests
import json
import insert

token = 'secret_qVw43sR9rdm11uwkMbYZ7Wo2gM9TixEsIjpFbB2ia58'

database_id = '03173c749bb340f79da67bd27718c890' # 신청자 명단
database_id_draw = '75dcbfd40c22412bb6cc1ed1cdc05047' # 대진표
database_id_final_apllicant = 'e9ee98f724f648d1b911396137729ce6' # 출전 확정자 명단

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
url = f'https://api.notion.com/v1/databases/{database_id_final_apllicant}/query'


response = requests.post(url, headers=headers)
data = response.json()
resp_data = data["results"]

# 확정자만 추출
resp_data = [item for item in resp_data if item.get('properties', {}).get('상태', {}).get('status', {}).get('name') == '확정']

# print(resp_data)

# print(resp_data[0]["id"]) # 페이지 id
# print(resp_data[0]["properties"]["상태"]["status"]["name"]) # 항목: 상태 (확정, 환불예정, 취소)
# print(resp_data[0]["properties"]["합산점수"]["number"]) # 항목: 합산점수
# print(resp_data[0]["properties"]["신청자명"]["title"][0]["text"]["content"]) # 항목: 신청자 명
# print(resp_data[0]["properties"]["파트너명"]["rich_text"][0]["text"]["content"]) # 항목: 파트너 명

refind_json = []

for idx, elem in enumerate(resp_data):

    temp_json = {}

    temp_json["id"] = elem["id"]
    temp_json["status"] = elem["properties"]["상태"]["status"]["name"]
    temp_json["totalscore"] = elem["properties"]["합산점수"]["number"]
    temp_json["mainnm"] = elem["properties"]["신청자명"]["title"][0]["text"]["content"]
    temp_json["subnm"] = elem["properties"]["파트너명"]["rich_text"][0]["text"]["content"]

    refind_json.append(temp_json)

# "totalscore" 키를 기준으로 정렬
sorted_json_data = sorted(refind_json, key=lambda x: x["totalscore"], reverse=True)

# print(len(sorted_json_data))

# 임시 섞기
def mixing_arr(my_list):
    result = []

    for i in range(len(my_list) // 2):
        result.append(my_list[i])
        result.append(my_list[-(i + 1)])

    # 배열의 길이가 홀수일 경우 중간 요소를 추가
    if len(my_list) % 2 != 0:
        result.append(my_list[len(my_list) // 2])

    return result

def generate_map(input_array):
    cnt = 1

    for i, value in enumerate(input_array):

        if i % 3 == 0 and i > 0:
            cnt += 1
        
        input_array[i]["jo"] = cnt

    if len(input_array) % 3 == 1:
        last_elem =  input_array[-1]

        # 키 이름 (변경)
        last_key = "jo"

        last_val = last_elem[last_key]

        # 키 이름 (변경)
        sec_last_key = "jo"
        
        input_array[len(input_array)-2][sec_last_key] = last_val

    return input_array

# print(generate_map(mixing_arr(sorted_json_data)))

for element in generate_map(mixing_arr(sorted_json_data)):

    nm = ""
    if(element["subnm"] != ""):
        nm = element["mainnm"] + ":" + element["subnm"]
    else:
        nm = element["mainnm"]

    insert.send_jo(element["jo"],nm)