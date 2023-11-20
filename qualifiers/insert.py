import requests

# API 엔드포인트 URL
url = 'https://api.notion.com/v1/pages'
your_notion_api_key = 'secret_qVw43sR9rdm11uwkMbYZ7Wo2gM9TixEsIjpFbB2ia58'

# 필요한 요청 헤더 설정
headers = {
    'Authorization': f'Bearer {your_notion_api_key}',  # NOTION_API_KEY 대신 실제 API 토큰 사용
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28',
}

def send_jo(jo,name):

    # 요청 본문 데이터 설정
    data = {
        'icon': {'type': 'external', 'external': {'url': 'https://www.notion.so/icons/checkmark_red.svg'}},
        "parent": {"database_id": "f848f54418e2478c814fc2c2c481b948"},
        "properties": {
            "이름": {
                "title": [  # 타이틀 (1조)
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            # "승자": {
            #     "multi_select": [  # 'title' 속성을 배열로 변경
            #         {
            #             "name": "이민형:최준한"
            #             , "color":"gray"
                        
            #         }
            #         ,{
            #             "name": "이미라:구미운"
            #             , "color":"red"
            #         }

            #     ]
            # },
            "그룹": {
                "select": {
                    "name": str(jo)+"조"
                }
            },
            "조": {
                "number": jo
            }
        }
    }

    # POST 요청을 사용하여 데이터베이스에 페이지 추가
    response = requests.post(url, headers=headers, json=data)

    # # 응답 내용 확인
    # print(response.status_code)
    # print(response.json())