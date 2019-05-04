from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from searchview.models import *
from parsing.views import *
import urllib.parse
import html
import cv2
import numpy as np
import base64
from decimal import Decimal

# Create your views here.
#대분류 - 소분류 - 기타
def error_message(request, type_code):
    message = ""
    if type_code == 1000:
        message = "등록되지 않은 서비스입니다."
    elif type_code == 2000:
        message = "준비중인 서비스입니다."
    elif type_code == 3000:
        message = "실행중 오류가 발생하였습니다."
    elif type_code == 4000:
        message = "연결을 실패하였습니다."
    elif type_code == 5000:
        message = "인자가 부족합니다."
    else:
        message = "예상치 못한 오류가 발생하였습니다."

    return render(request, 'error.html', {"error_code":type_code, "content":message})

def get_service_name(library):
    try:
        company = Company.objects.get(company_nm=library)
        return company
    except:
        return False

def get_service_opiton(register_id):
    try:
        rows = LibraryOpiton.objects.filter(company_fk=register_id)
        option_list = []
        for item in rows:
            add_list = {"name":item.option_name, "value":item.search_option}
            option_list.append(add_list)
        
        return option_list
    except:
        return False

def search_library(request, library, keyword, page_number = "1", options = "null"):
    company = get_service_name(library)
    if company is False:
        return error_message(request, 1000)
    option = get_service_opiton(company.register_id)
    
    if option is False:
        return error_message(request, 3000)

    data = {
        "company_nm" : company.company_nm,
        "keyword" : keyword,
        "register_id" : company.register_id,
        "search_option" : option,
        "page_number": 1
    }
    result = \
        library_search(id=company.register_id, \
        keyword=keyword, \
        page_number=page_number, \
        search_option=options)
    page_number_of_result = int(result["number_of_result"])
    if result["number_of_result"] % 20 !=0:
        page_number_of_result+=1
    result["page_number_of_result"] = page_number_of_result
    result["options"] = options
    data.update(result)
    return render(request, "search_view.html", data)

def search_option(request):
    try:
        library = request.POST['company_nm']
        keyword = request.POST['keyword']
        page_number = request.POST['page_number']
        option = request.POST['search_option']
    except:
        return error_message(request, "5000")
    return search_library(request, library, keyword, page_number, option)


def draw_map(width, height, cur):
    img_width = 300
    img_height = 300
    line_color = (99,151,255)
    img = np.zeros((img_width,img_height,3), np.uint8)
    img.fill(255)
    cv2.rectangle(img, (0,0),(img_width,img_height),line_color, 3)

    start_y = 0
    start_x = 0
    x_gap = int(img_width/width)
    y_gap = int(img_height/height)
    #가로줄 긋기
    for i in range(height-1):
        cv2.line(img, (0,start_y+y_gap),(img_width,start_y+y_gap),line_color, 3)
        start_y += y_gap
    
    #세로줄 긋기
    for i in range(width-1):
        cv2.line(img, (start_x+x_gap,0),(start_x+x_gap,img_height), line_color, 3)
        start_x += x_gap

    #행, 열
    row = 0
    col = 0
    #책이 위치하는 곳 좌표 구하기
    circle_x = x_gap * int(cur/(height)) - int(x_gap/2)
    col = int(cur/height)
    if int(cur%height) !=0:
        circle_x += x_gap
        col+=1

    circle_y = y_gap * int(cur%(height)) - int(y_gap/2)
    row = int(cur%height)
    if cur%height == 0:
        circle_y = img_height - int(y_gap/2)
        row = height
    if circle_y <= 0:
        circle_y = int(y_gap/2)
    #책이 위치하는 곳 그리기
    cv2.circle(img, (circle_x, circle_y), 10, (97,76,255), -1)
    
    #문구삽입
    cv2.putText(img, "here", (circle_x-3, circle_y-3), cv2. cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1, (0,0,0))

    img =cv2.imencode(".png", img)[1]
    return img, row, col


def search_book_location(request, library, isbn):
    company = get_service_name(library)
    if company is False:
        return error_message(request, 1000)
    data = {
        "company_nm" : company.company_nm,
        "register_id" : company.register_id,
        "data" : "No"
    }
    try:
        data["keyword"] = Isbn.objects.get(isbn = isbn).book_nm
    except:
        return error_message(request, 3000)

    try:
        book = Book.objects.select_related()\
            .filter(isbn=isbn, \
            nfc_id_fk=Nfc.objects.filter(company_fk=data["register_id"])[0]).\
            order_by('-update_date')
    except Exception as e:
        #return error_message(request, 3000)
        return render(request, "location_view.html", data)  

    if len(book) == 0:
        return render(request, "location_view.html", data)  

    try:
        data["nfc_info"] = book[0].nfc_id_fk.shelf_location
        data["bookshelf_height"] = book[0].nfc_id_fk.shelf_height
        data["bookshelf_width"] = book[0].nfc_id_fk.shelf_width
        data["nfc_image"] = book[0].nfc_id_fk.image_source
        data["book_location"] = book[0].book_location
        data["book_image"] = book[0].image_source
        data["update"] = book[0].update_date
        data["keyword"] = book[0].title
        data["data"] = "Yes"
    except Exception as e:
        return error_message(request, 3000)
    img, row, col = draw_map(int(data["bookshelf_width"])\
        ,int(data["bookshelf_height"])\
        ,int(data["book_location"]))
    img = base64.b64encode(img)
    data["book_img"] = str(img)[2:-1]
    data["row"] = row
    data["col"] = col
    #return HttpResponse(img, content_type='image/jpg')
    return render(request, "location_view.html", data)


def search_all(request, keyword):
    try:
        book = Book.objects.filter(title__contains = keyword)
        data = dict()
        company_list = list()
        data["noData"] = "Yes"
        for idx, item in enumerate(book):
            if item.nfc_id_fk.company_fk.latitude is None:
                continue
            if item.nfc_id_fk.company_fk.longitude is None:
                continue
            data["noData"] = "No"
            add = {
                "no" : idx + 1,
                "name" : item.nfc_id_fk.company_fk.company_nm,
                "address" : item.nfc_id_fk.company_fk.address,
                "latitude" : Decimal(item.nfc_id_fk.company_fk.latitude),
                "longitude" : Decimal(item.nfc_id_fk.company_fk.longitude),
            }
            company_list.append(add)
        data["keyword"] = keyword
        data["list"] = company_list
    except Exception as e:
        print(e)
        return error_message(request, 3000)
    
    return render(request, "search_all.html", data)