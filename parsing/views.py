from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from parsing.models import *
from parsing.program import *
import json

# Create your views here.

def get_service(service):
    try:
        item = Company.objects.get(register_id=service)
        return item.service_nm
    except:
        return 0

def library_search(id, keyword, page_number = 1, search_option = "null"): 
    service = get_service(id)

    if(service == "ChungbukNational"):
        service = ChungbukNational.ChungbukNational()
    else:
        return 0

    try:
        service.setting(keyword=keyword, page_number = page_number, search_type=search_option,)
        number_of_results, data = service.show()
        direct_url = service.direct_URL
    except:
        return 1

    return dict(
        {
            "number_of_result" : number_of_results,
            "page_number" : int(page_number),
            "book_list" : data,
            "url" : direct_url,
        }
    )

def kakao_search(service_nm, keyword):
    service = get_service(service_nm)
    if(service == "ChungbukNational"):
        service = ChungbukNational.ChungbukNational()
    else:
        return dict({
            "number_of_result": 0
        })
    service.setting(keyword=keyword)
    number_of_result, result = service.min()
    return dict(
        {
            "number_of_result" : number_of_result,
            "book_list" : result,
        }
    )