from parsing.program.BookDataType import *
import unicodedata
import re
from parsing.models import *
from django.db.models import Q

class Crawler:
    pattern = re.compile('((GS1|gs1)*)([0-9]+)([X|x]*)')
    year_pattern = re.compile('[0-9]{4}')
    def __init__(self):
        self.keyword = ""
        self.dataList = list()
        self.number_of_result = int(0)
        self.direct_URL = str("")
        self.sqlResult = list()
        self.fast = False
    
    def addData(self, data):
        if type(data) != BookDataType:
            raise Exception("Type Error")
        self.dataList.append(data)
    
    def do_crawling(self, keyword, page_number, search_type):
        self.dataList.clear()
        try:
            if len(self.sqlResult) == 0:
                self.sqlResult = Isbn.objects.filter(
                    Q(book_nm__icontains=keyword) | Q(keyword__icontains=keyword)
                )
                self.sqlResult = list(self.sqlResult)
            else:
                pass
        except:
            pass
    
    def setting(self, keyword, page_number = 1, search_type = "null"):
        self.keyword = keyword
        self.page_number = page_number
        self.search_type = search_type
        
    def min(self):
        self.fast = True
        self.do_crawling(self.keyword, self.page_number, self.search_type)
        result = list()
        for idx, item in enumerate(self.dataList):
            temp = {"title": item.title, \
             "author": item.author, \
             "publisher": item.publisher, \
             "year": item.year, \
             "status": unicodedata.normalize('NFC', item.status), \
             "place" : unicodedata.normalize('NFC', item.place), \
             "callNumber" : unicodedata.normalize('NFC', item.callNumber)}
            result.append(temp)
        return self.number_of_result, result

    def show(self):
        self.fast = False
        self.do_crawling(self.keyword, self.page_number, self.search_type)
        result = list()
        for item in self.dataList:
            temp = {"title": item.title, \
             "imgSrc": item.imgSrc, \
             "author": item.author, \
             "publisher": item.publisher, \
             "year": item.year, \
             "status": unicodedata.normalize('NFC', item.status), \
             "place" : unicodedata.normalize('NFC', item.place), \
             "callNumber" : unicodedata.normalize('NFC', item.callNumber), \
             "href" : item.href, \
             "isbn" : item.isbn }
            result.append(temp)

        return self.number_of_result, result
    def get_pattern_year(self, year):
        if year is None:
            year = "0000"
        else:
            year = year.replace(' ', '')
        return year
            
    def get_isbn_re(self, isbn, title, author, year):
        isbn = self.pattern.search(str(isbn))

        if isbn is not None:
            try:       
                isbn = (isbn).group(0)
            except:
                return None
                
            try:
                item = Isbn.objects.get(isbn=isbn)
                if self.keyword in item.keyword:
                    pass
                else:
                    item.keyword += "|" + self.keyword
                    item.save()
            except:
                try:
                    item = Isbn(isbn=isbn, book_nm=title, author=author, publish_year=year, keyword=self.keyword)
                    item.save()
                except:
                    pass
        return isbn