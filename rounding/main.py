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
url = f'https://api.notion.com/v1/databases/{database_id_draw}/query'


response = requests.post(url, headers=headers)
data = response.json()
resp_data = data["results"]

chk_resp_data = [item for item in resp_data if item.get('properties', {}).get('승자', {}).get('status', {}).get('name') == '미정']

## 검증역역 - 시작

if(len(chk_resp_data) > 0):
    alert_msg = "경기 결과 미등록 출전자 명단:\n"
    for rsep_elem in chk_resp_data:
        alert_msg += "\t- "+str(rsep_elem["properties"]["이름"]["title"][0]["text"]["content"])+"\n"
    alert_msg += "위 출전자들의 경기 결과(승자)를 기록 후 다시 수행하세요"
    print(alert_msg)
    exit() #테스트종료

# '조' 키가 가지고 있는 값들을 추출합니다.
validation_values = [temp_storage["properties"]['팀']['number'] for temp_storage in resp_data]
# None 값 제거
validation_values = [x for x in validation_values if x is not None]
# 중복을 제거하고 오름차순으로 정렬합니다.
validation_sorted_values = sorted(set(validation_values))

for target_team in validation_sorted_values:
    inner_validation_values = [item for item in resp_data if item.get('properties', {}).get('팀', {}).get('number', {}) == target_team]
    inner_final_validation_values = [temp_storage["properties"]['승자']['status']['name'] for temp_storage in inner_validation_values]
    if inner_final_validation_values.count('승') > 1:
        print("한 경기에 승자가 두 팀이 존재 할 수 없습니다. \n \t-\t"+str(target_team)+"target_team")
        exit() #테스트종료
    else:
        # 아마 위에서 처리 되겠지만 추가적인 조치
        print("경기 결과가 아직 기록되지 않은 팀입니다. \n \t-\t"+str(target_team)+"target_team")
        exit() #테스트종료

## 검증역역 - 종료 ++ BYE가 '패'가 아니면 안 되게 검증 필요

resp_data = [item for item in resp_data if item.get('properties', {}).get('승자', {}).get('status', {}).get('name') == '승']

refind_json = []

for idx, elem in enumerate(resp_data):

    temp_json = {}

    temp_json["id"] = elem["id"]
    temp_json["totalscore"] = elem["properties"]["점수"]["number"]
    temp_json["team"] = elem["properties"]["이름"]["title"][0]["text"]["content"]

    refind_json.append(temp_json)


# "totalscore" 키를 기준으로 정렬
sorted_json_data = sorted(refind_json, key=lambda x: x["totalscore"], reverse=True)

new_array = []

while sorted_json_data:
    # 첫 번째 항목을 pop하고 새로운 배열에 append
    new_array.append(sorted_json_data.pop(0))

    # 맨 마지막 항목을 pop하고 새로운 배열에 append
    new_array.append(sorted_json_data.pop(-1))

# print(new_array)

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
            requests.post(url, headers=headers, json=generate_data_frame(teams[0],tpp,"승",temp_idx))
            teams.pop(0)
            #삽입

            requests.post(url, headers=headers, json=generate_data_frame_BYE(tpp,temp_idx))
            #삽입 (BYE)

        else:
            requests.post(url, headers=headers, json=generate_data_frame(teams[0],tpp,"미정",temp_idx))
            teams.pop(0)
            #삽입

            requests.post(url, headers=headers, json=generate_data_frame(teams[0],tpp,"미정",temp_idx))
            teams.pop(0)
            #삽입
        
        if(len(teams)!=0):
            requests.post(url, headers=headers, json=generate_data_frame_LINE(tpp))
            #삽입(남은teams의 len이 0이면 X)

def generate_data_frame(data, tpp, win,tidx):

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
            },
            "팀": {
                "number": tidx
            }
        }
    }

    return data_re

def generate_data_frame_BYE(tpp,tidx):

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
            },
            "팀": {
                "number": tidx
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

generate_bracket(new_array)