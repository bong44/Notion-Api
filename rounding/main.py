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

if(len(resp_data)<1):
    print('예선 -> 본선대진 작성 후 수행가능합니다.')
    exit() #테스트종료

# '라운드' 키가 가지고 있는 값들을 추출합니다.
all_round_values = [temp_storage['properties']['라운드']['multi_select'][0]['name'] for temp_storage in resp_data]
# 중복을 제거하고 오름차순으로 정렬합니다
all_round_values = sorted(set(all_round_values))

try:
    all_round_values = [int(item.replace('강', '')) for item in all_round_values]
except Exception as e:
    # 예상하지 못한 다른 예외가 발생한 경우 처리할 코드를 작성합니다.
    print(f"매치가 종료되었습니다. \n(새로운 매치를 위해선 모든 항목을 삭제해 주세요)")
    exit() #테스트종료

find_lowest_round = str(sorted(all_round_values)[0])+'강'

resp_data = [item for item in resp_data if item.get('properties', {}).get('라운드', {}).get('multi_select', {})[0].get('name') == find_lowest_round]

# BYE 있는 라운드인지 플레그 설정
bye_check = [temp_storage['properties']['이름']['title'][0]['text']['content'] for temp_storage in resp_data]
bye_check = sorted(set(bye_check))

# 'BYE'가 배열에 있는지 여부를 확인 (전역변수로 사용)
bye_check_result = 'BYE' in bye_check

chk_resp_data = [item for item in resp_data if item.get('properties', {}).get('승자', {}).get('status', {}).get('name') == '미정']

## 검증역역 - 시작

if(len(chk_resp_data) > 0):
    alert_msg = "경기 결과 미등록 출전자 명단:\n"
    for rsep_elem in chk_resp_data:
        alert_msg += "\t- "+str(rsep_elem["properties"]["이름"]["title"][0]["text"]["content"])+"\n"
    alert_msg += "위 출전자들의 경기 결과(승자)를 기록 후 다시 수행하세요"
    print(alert_msg)
    exit() #테스트종료

# '팀' 키가 가지고 있는 값들을 추출합니다.
validation_values = [temp_storage["properties"]['팀']['number'] for temp_storage in resp_data]
# None 값 제거
validation_values = [x for x in validation_values if x is not None]
# 중복을 제거하고 오름차순으로 정렬합니다.
validation_sorted_values = sorted(set(validation_values))

for target_team in validation_sorted_values:
    inner_validation_values = [item for item in resp_data if item.get('properties', {}).get('팀', {}).get('number', {}) == target_team]
    inner_final_validation_values = [temp_storage["properties"]['승자']['status']['name'] for temp_storage in inner_validation_values]
    if inner_final_validation_values.count('승') > 1:
        print("한 경기에 승자가 두 팀이 존재 할 수 없습니다. \n \t "+str(target_team)+"번 팀")
        exit() #테스트종료
    elif inner_final_validation_values.count('미정') > 0:
        # 아마 위에서 처리 되겠지만 추가적인 조치
        print("경기 결과가 아직 기록되지 않은 팀입니다. \n \t- "+str(target_team)+"번 팀")
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


if(bye_check_result):
    #BYE 존재 배열 섞기
    # "totalscore" 키를 기준으로 정렬
    sorted_json_data = sorted(refind_json, key=lambda x: x["totalscore"], reverse=True)

    new_array = []

    while sorted_json_data:
        # 첫 번째 항목을 pop하고 새로운 배열에 append
        new_array.append(sorted_json_data.pop(0))

        # 맨 마지막 항목을 pop하고 새로운 배열에 append
        new_array.append(sorted_json_data.pop(-1))

else:
    #BYE 없음 기존 순서대로
    new_array = refind_json


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
    if(bye_teams + len(teams) == 2):
        tpp = "결승"
    else:
        tpp = str(bye_teams + len(teams))+"강"

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

    jo_num = data["totalscore"]


    # 요청 본문 데이터 설정
    data_re = {
        'icon': {'type': 'external', 'external': {'url': 'https://www.notion.so/icons/checkmark_red.svg'}},
        "parent": {"database_id": "75dcbfd40c22412bb6cc1ed1cdc05047"},
        "properties": {
            "이름": {
                "title": [  # 'title' 속성을 배열로 변경
                    {
                        "text": {
                            "content": data["team"]
                        }
                    }
                ]
            },
            "라운드": {
                "multi_select": [  # 'title' 속성을 배열로 변경
                    {
                        "name": tpp
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
                "number": jo_num
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
                        "name": tpp
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
                        "name": tpp
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