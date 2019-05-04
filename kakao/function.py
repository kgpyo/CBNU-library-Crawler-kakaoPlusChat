import pymysql
from kakao.models import *
from django.db.models import Q
import datetime
    #10, 20, 30, 40, 50, 60
buttons = {
    "type":"buttons",
    "buttons": ["통합검색","지정검색","검색설정","질문하기","답변보기"]
}

text_buttons = {
    "type":"text"
}
def delete_chat_rootm(user_key):
    try:
        Qna.objects.filter(userkey_fk=user_key).delete()
        User.objects.filter(userkey_id=user_key).delete()
        return True
    except:
        return False

def check_new_user(user_key):
    try:
        #기존 유저가 있는지 검색
        User.objects.get(userkey_id=user_key)
    except:
        #없으면 유저를 새로 등록
        try:
            User(userkey_id=user_key, library=0, user_status=0).save()
        except:
            return False
    return True

def check_user_status(user_key):
    try:
        user = User.objects.get(userkey_id=str(user_key))
        if user.library is 0:
            return user.user_status, user.library, False
        library = Company.objects.get(register_id=user.library)
        return user.user_status, user.library, library.company_nm
    except:
        return False, False, False

def update_user_status(user_key, status, library = None):
    try:
        if library is None:
            User.objects.filter(userkey_id=user_key).update(user_status = status)   
        else:
            try:
                Company.objects.get(register_id=library)
            except:
                User.objects.filter(userkey_id=user_key).update(user_status = 0, library = 0)   
                return False
            User.objects.filter(userkey_id=user_key).update(user_status = status, library=library)   
    except:
        return False
    return True

#답변보기
def get_answer(user_key):
    message = "[작성한 질문 확인하기]\n"  +\
        "최근 작성하신 3개의 게시글만 조회가능합니다.\n\n"
    try:
        qna = Qna.objects.select_related('library_fk').filter(userkey_fk=user_key).order_by('-created')
        for idx, content in enumerate(qna):
            if idx == 3:
                break
            
            message += "[" + content.library_fk.company_nm + "]\n"
            message += "◆" + str(content.created) + "등록\n"
            message += "   " + content.content + "\n"
            if content.answerdate is not None:
                message += "└ 답변 : " + str(content.answerdate) + "\n"
                answer = ""
                if content.answer is None:
                    answer = "--"
                else:
                    answer = content.answer
                message += answer + "\n"
            else:
                message += "└ 등록된 답변 없음\n"
            message += "===============\n"
    except:
        message += "조회중 오류가 발생하였습니다."
    return message

def get_message(result):
    if result["number_of_result"] == 0:
        msg = "검색결과 없음\n핵심단어를 띄어 써 주시면 통합검색 명을 모두 입력 하는 것보다 쉽게 찾을 수 있습니다. "
        return msg
    msg = str(result["number_of_result"]) + "건 검색\n"
    for book in result["book_list"]:
        title = book["title"]
        if len(title) >18:
            title = title[:15] + "..."
        msg += "\n◆" + title + "\n"
        msg += " ▷ " + book["publisher"] + "\n"
        msg += " ▷ " + book["author"] + "/" + book["year"] +"\n" 
        msg += " ▷ " + book["place"] + "\n"
        msg += " ▷ " + book["status"] + "[" + book["callNumber"] + "]\n"
    return msg


def get_library(library):
    try:
        company = Company.objects.filter(company_nm__contains=library)
        if len(company) == 0:
            return False, False
        message = "등록하시려는 서점의 번호를 입력하세요.\n"
        message += "번호 / 서점명 - 주소 순서입니다.\n\n"
        for item in company:
            message += "■" + str(item.register_id) + "/" + str(item.company_nm) + "\n"
            message += str(item.address) + "\n\n"
        return message, True
    except:
        return False, False

def write_question(user_key, library, content):
    try:
        company = Company.objects.get(register_id=library)
        qna = Qna(userkey_fk=user_key, library_fk=company, content=content)
        qna.save()
        return True
    except:
        return False