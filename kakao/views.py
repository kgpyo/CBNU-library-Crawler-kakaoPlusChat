from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import re
import urllib.parse
import requests
import json
from kakao.function import *
from parsing.views import *
import os
# Create your views here.

def keyboard(request):
    return JsonResponse(buttons)

def get_image(request, image_name):
    link = os.path.join(os.getcwd(),"media/" + image_name)
    images = []
    image_data = open(link, "rb").read()
    images.append(image_data)
    return HttpResponse(images,content_type="image/png")

@csrf_exempt
def remove_data(request, user_key):
    delete_chat_rootm(user_key)
    return JsonResponse({"type":"text"})

@csrf_exempt
def answer(request):
    json_str = (request.body).decode('utf-8')
    received_json = json.loads(json_str)
    content = received_json['content']
    content_type = received_json['type']
    user_key = received_json['user_key']

    if content_type == "photo":
        return JsonResponse({
            "message": {"text":"지원하지 않는 기능입니다."},
            "keyboard":buttons
        })

    #채팅방 입장
    if check_new_user(user_key) is False:
        return JsonResponse({
            "message":{"text":"사용자등록에 오류가 발생하였습니다.\n채팅방을 완전히 나가신후 다시 접속해주세요."},
            "keyboard":buttons
        })
    
    
    #현재 유저 상태 확인
    status, library, library_nm = check_user_status(user_key)

    #메뉴 선택단계
    if status == 0:
        message = " "
        input_type = text_buttons
        image = "None"
        if content == "통합검색":
            update_user_status(user_key, 10)
            message = "찾고자 하는 도서명을 입력하시면, 해당 재고가 있는 서점을 출력합니다."
            image = "allsearch.jpg"
        elif content == "답변보기":
            update_user_status(user_key, 0)
            message = get_answer(user_key)
            input_type = buttons
        elif content == "검색설정":
            update_user_status(user_key, 30)
            message = "검색설정 혹은 질문하실 서점을 등록합니다.\n" \
                + "서점명을 모두 입력하시는 것보다 핵심단어를 입력해주시면 쉽게 찾으실수 있습니다."
            image = "setting.jpg"
        elif library == 0:
            message = "\"검색설정\"을 통해  먼저 사용하실 서점을 등록하세요."
            input_type = buttons
        elif content == "지정검색":
            update_user_status(user_key, 20)
            message = "검색설정을 통해 설정하신 서점을 기준으로 도서를 검색합니다.\n"
            message = message + "핵심단어를 띄어 써 주시면 통합검색 명을 모두 입력 하는 것보다 쉽게 찾을 수 있습니다."
            image = "search.jpg"
        elif content == "질문하기":
            update_user_status(user_key, 40)
            message = "도서관 이용에 관련된 문의를 작성하고 전송버튼을 누르시면 등록이 완료됩니다.\n"
            message += "기타 본 도서 검색관련 서비스이용에 관련된 문의는 서비스 관리자에게 문의하세요."
            image = "qna.jpg"
        if image == "None":
            return JsonResponse({
                "message":{
                    "text" : message,
                },
                "keyboard":input_type    
            })
        return JsonResponse({
            "message":{
                "text" : message,
                "photo": {
                    "url":"https://xn--c79as89achap9v.kr/kakao/get/images/" + image,
                    "width": 300,
                    "height": 100
                }
            },
            "keyboard":input_type
        })

    #통합검색
    if status == 10:
        update_user_status(user_key, 0)
        message = "모바일 브라우저에서 실행합니다.\n"
        message += "위치정보는 현재 위치에서 가장 가까운 서점순서로 출력하기 위함입니다.\n"
        message += "해당 목적 이외에 수집하지 않습니다."
        return JsonResponse({
            "message": {
                "text" : message,
                "message_button": {
                    "label" : str(content) + "검색",
                    "url" : str("https://서점검색.한국/all/") + str(content)
                }
            },
            "keyboard":buttons
        })
    
    #지정검색
    if status == 20:
        update_user_status(user_key, 0)
        result = kakao_search(library, content)
        message = get_message(result)
        return JsonResponse({
            "message":{
                "text":message,
                "message_button": {
                    "label" :"검색결과 더보기",
                    "url" : "https://서점검색.한국/search/" + library_nm + "/" + str(content)
                }
            },
            "keyboard":buttons
        })
    
    #검색설정
    if status == 30:
        message, result = get_library(content)
        if result is False:
            update_user_status(user_key, 0)
            return JsonResponse({
                "message": {
                    "text":"검색결과가 없습니다. 처음상태로 돌아갑니다."
                },
                "keyboard":buttons
            })
        else:
            if update_user_status(user_key, 31) is False:
                return JsonResponse({
                    "message": {
                        "text":"사용자 상태 업데이트중에 오류가 발생하였습니다.\n채팅방 나가기를 통해 대화내용 삭제 후 다시 방문해주세요.",
                    },
                    "keyboard":buttons
                })
            return JsonResponse({
                "message": {
                    "text": message,
                },
                "keyboard":text_buttons
            })

    #서점선택
    if status == 31:
        if update_user_status(user_key, 0, content) is False:
            return JsonResponse({
                "message":{
                    "text":"사용자 상태 업데이트중에 오류가 발생하였습니다.\n유효하지 않은 번호를 입력하지 않았는지 확인해주시기 바랍니다.\n채팅방 나가기를 통해 대화내용 삭제 후 다시 방문해주세요."
                },
                "keyboard":buttons
            })
        else:
            return JsonResponse({
                "message":{
                   "text": "정상적으로 등록이 완료되었습니다."
                },
                "keyboard":buttons
            })

    #질문하기
    if status == 40:
        update_user_status(user_key, 0)
        if write_question(user_key, library, content) is True:
            return JsonResponse({
                 "message":{
                    "text":"정상 등록되었습니다. 문의하신 내용을 확인하시려면 답변보기 메뉴를 통해 확인하실수 있습니다.\n"+
                    "채팅방을 나가실 경우 작성하신 모든 문의 내용이 삭제됩니다.",
                },
                "keyboard":buttons
            })
        else:
            return JsonResponse({
                "message":{
                    "text":"등록에 실패하였습니다.",
                },
                "keyboard":{
                    "type":buttons
                }
            })        