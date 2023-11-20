import requests
import json
import math


token = 'secret_qVw43sR9rdm11uwkMbYZ7Wo2gM9TixEsIjpFbB2ia58'

database_id = '03173c749bb340f79da67bd27718c890' # 신청자 명단
database_id_draw = '75dcbfd40c22412bb6cc1ed1cdc05047' # 대진표
database_id_final_apllicant = 'e9ee98f724f648d1b911396137729ce6' # 출전 확정자 명단
database_id_final_qualifi = 'f848f54418e2478c814fc2c2c481b948' # 예선

headers = {
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}
url = f'https://api.notion.com/v1/databases/{database_id_final_qualifi}/query'


response = requests.post(url, headers=headers)
data = response.json()
resp_data = data["results"]

# '조' 키가 가지고 있는 값들을 추출합니다.
values = [temp_storage["properties"]['조']['number'] for temp_storage in resp_data]

# 중복을 제거하고 오름차순으로 정렬합니다.
unique_sorted_values = sorted(set(values))

refind_first_team = []
refind_second_team = []

# 존재하는 조 만큼 반복
for idx, elem in enumerate(unique_sorted_values):


    # 조 별로 1,2위 추출
    temp_jo_group = [item for item in resp_data if item.get('properties', {}).get('조', {}).get('number', {}) == elem]
    temp_jo_group1 = [item for item in temp_jo_group if item.get('properties', {}).get('순위', {}).get('select', {}).get('name', {}) in ['1위']]
    temp_jo_group2 = [item for item in temp_jo_group if item.get('properties', {}).get('순위', {}).get('select', {}).get('name', {}) in ['2위']]

    refind_first_team.append(temp_jo_group1[0])
    refind_second_team.append(temp_jo_group2[0])


# unique_sorted_values <-- 이 배열에 keys 담겨있음

# print(len(refind_first_team))
# print(len(refind_second_team))

sum_team_arr = refind_first_team + refind_second_team

# print(len(sum_team_arr))


# print(resp_data[0]["id"]) # 페이지 id
# print(resp_data[0]["properties"]["상태"]["status"]["name"]) # 항목: 상태 (확정, 환불예정, 취소)
# print(resp_data[0]["properties"]["합산점수"]["number"]) # 항목: 합산점수
# print(resp_data[0]["properties"]["신청자명"]["title"][0]["text"]["content"]) # 항목: 신청자 명
# print(resp_data[0]["properties"]["파트너명"]["rich_text"][0]["text"]["content"]) # 항목: 파트너 명


# for idx, elem in enumerate(resp_data):

#     temp_json = {}

#     temp_json["id"] = elem["id"]
#     temp_json["status"] = elem["properties"]["상태"]["status"]["name"]
#     temp_json["totalscore"] = elem["properties"]["합산점수"]["number"]
#     temp_json["mainnm"] = elem["properties"]["신청자명"]["title"][0]["text"]["content"]
#     temp_json["subnm"] = elem["properties"]["파트너명"]["rich_text"][0]["text"]["content"]

#     refind_json.append(temp_json)

# "totalscore" 키를 기준으로 정렬
# sorted_json_data = sorted(refind_json, key=lambda x: x["totalscore"], reverse=True)

# print(len(sorted_json_data))

def generate_bracket(teams):

    # API 엔드포인트 URL (대진표 삽입)
    url = 'https://api.notion.com/v1/pages'
    your_notion_api_key = 'secret_qVw43sR9rdm11uwkMbYZ7Wo2gM9TixEsIjpFbB2ia58'

    # 필요한 요청 헤더 설정
    headers = {
        'Authorization': f'Bearer {your_notion_api_key}',  # NOTION_API_KEY 대신 실제 API 토큰 사용
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
    }


    # 입력된 팀의 수를 2의 거듭제곱으로 만들기 위해 다음으로 큰 2의 거듭제곱 계산
    next_power_of_two = int(math.pow(2, math.ceil(math.log2(len(teams)))))

    # bye를 부여할 팀의 수 계산
    bye_teams = next_power_of_two - len(teams)

    temp_idx = 0

    # 1라운드 강수
    tpp = bye_teams + len(teams)

    # 대진표 생성
    while teams:  # 리스트가 비어 있지 않은 동안 반복
        temp_idx = temp_idx + 1

        # requests.post(url, headers=headers, json=generate_data_frame_LINE(tpp))
        #삽입 (vs)

        if temp_idx <= bye_teams:
            requests.post(url, headers=headers, json=generate_data_frame(teams[0],tpp,"승"))
            teams.pop(0)
            #삽입

            requests.post(url, headers=headers, json=generate_data_frame_BYE(tpp))
            #삽입 (BYE)

        else:
            requests.post(url, headers=headers, json=generate_data_frame(teams[0],tpp,"미정"))
            teams.pop(0)
            #삽입

            requests.post(url, headers=headers, json=generate_data_frame(teams[0],tpp,"미정"))
            teams.pop(0)
            #삽입
        
        if(len(teams)!=0):
            requests.post(url, headers=headers, json=generate_data_frame_LINE(tpp))
            #삽입(남은teams의 len이 0이면 X)

def generate_data_frame(data, tpp, win):

    original_string = data["properties"]["순위"]["select"]["name"]
    jo_num = data["properties"]["조"]["number"]

    # 문자열을 슬라이싱하여 "1"을 가져오기
    number_part = original_string[:-1]

    # 숫자로 변환하기
    result_number = int(number_part)

    # 요청 본문 데이터 설정
    data_re = {
        'icon': {'type': 'external', 'external': {'url': 'https://www.notion.so/icons/checkmark_red.svg'}},
        "parent": {"database_id": "75dcbfd40c22412bb6cc1ed1cdc05047"},
        "properties": {
            "이름": {
                "title": [  # 'title' 속성을 배열로 변경
                    {
                        "text": {
                            "content": data["properties"]["이름"]["title"][0]["text"]["content"]
                        }
                    }
                ]
            },
            "라운드": {
                "multi_select": [  # 'title' 속성을 배열로 변경
                    {
                        "name": str(tpp)+"강"
                        , "color":"gray"
                    }
                ]
            },
            "승자": {
                "status": {
                    "name": win
                }
            },
            "점수": {
                "number": result_number+jo_num
            }
        }
    }

    return data_re

def generate_data_frame_BYE(tpp):

    # 요청 본문 데이터 설정
    data_re = {
        'icon': {'type': 'external', 'external': {'url': 'https://www.notion.so/icons/checkmark_blue.svg'}},
        "parent": {"database_id": "75dcbfd40c22412bb6cc1ed1cdc05047"},
        "properties": {
            "이름": {
                "title": [  # 'title' 속성을 배열로 변경
                    {
                        "text": {
                            "content": "BYE"
                        }
                    }
                ]
            },
            "라운드": {
                "multi_select": [  # 'title' 속성을 배열로 변경
                    {
                        "name": str(tpp)+"강"
                        , "color":"gray"
                    }
                ]
            },
            "승자": {
                "status": {
                    "name": "패"
                }
            }
        }
    }

    return data_re
def generate_data_frame_LINE(tpp):

    # 요청 본문 데이터 설정
    data_re = {
        "parent": {"database_id": "75dcbfd40c22412bb6cc1ed1cdc05047"},
        "properties": {
            "이름": {
                "title": [  # 'title' 속성을 배열로 변경
                    {
                        "text": {
                            "content": "—————————————————"
                        }
                    }
                ]
            },
            "라운드": {
                "multi_select": [  # 'title' 속성을 배열로 변경
                    {
                        "name": str(tpp)+"강"
                        , "color":"gray"
                    }
                ]
            },
            "승자": {
                "status": {
                    "name": "패"
                }
            }
        }
    }

    return data_re


generate_bracket(sum_team_arr)