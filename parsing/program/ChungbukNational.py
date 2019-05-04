from . import crawler
from bs4 import BeautifulSoup #need pip install Beautifulsoup, bs4
import json
import requests
import re
import urllib.parse
from parsing.program.BookDataType import *
from parsing.models import *
from multiprocessing import Pool 
import django

class ChungbukNational (crawler.Crawler):
    CONST_URL = 'http://cbnul.chungbuk.ac.kr/search/Search.Result.ax?sid=1&q='
    CONST_RESULT_URL = 'http://cbnul.chungbuk.ac.kr/search/'
    CONST_PAGE_URL = "&page="
    #CONST_PAGE_TYPE = ("", "&f=(BR%3A%26quot%3B01%26quot%3B)", "&f=(BR%3A%26quot%3B02%26quot%3B)", "&f=(BR%3A%26quot%3B03%26quot%3B)", "&f=(BR%3A%26quot%3B04%26quot%3B)")
    #CONST_PAGE_NAME = Enum(ALL, CENTER, SCI, MEDI, LAW)
    CONST_NO_IMAGE = "http://cbnul.chungbuk.ac.kr/images/search/bg_book_shadow.png"
    
    #override
    def do_crawling(self, keyword, page_number = 1, search_type = "null"):
        super().do_crawling(keyword, page_number, search_type)
        page_number = self.page_number
        self.direct_URL = "http://cbnul.chungbuk.ac.kr/search/Search.Result.ax?sid=1&q=" 
        #+ urllib.parse.quote(keyword)
        self.URL = self.CONST_URL + urllib.parse.quote(keyword) \
            + self.CONST_PAGE_URL + str(page_number)
            #self.CONST_PAGE_TYPE[search_type]
        if search_type != "null":
            self.URL += "&" + search_type
        self.dataList.clear()
        self.parse()
        
        return self.dataList
    
    def parse(self):
        resp = requests.get(self.URL)
        if resp.status_code == 200:
            self.html = resp.text
        else:
            raise Exception("접속 오류")

        #전체 검색 결과의 개수 확인
        soup = BeautifulSoup(self.html, 'html.parser')
        number_of_result = soup.find("div",{"class":"searchTitle5"})\
            .find("h3").find("span").text
        self.number_of_result = int(number_of_result[1:(number_of_result.find("건"))])

        #책 정보 확인하여 리스트에 담기
        book_list = soup.find("div",{"id":"result_view"})\
            .find_all("div", {"class":"textArea2"})
        count = 0
        for book in book_list:
            newData = BookDataType()
            book_info = book.find("div",{"class":"body"})
            newData.imgSrc = self.get_book_image(book.find("img"))
            newData.title, newData.href = self.get_book_title(book_info.find("a",{"class":"title"}))
            newData.author, newData.publisher, newData.year = self.get_book_info(book_info)        
            newData.year = self.get_pattern_year(newData.year)
            newData.place, newData.status, newData.callNumber = self.get_book_call_number(book_info)
            newData.href = self.CONST_RESULT_URL + newData.href
            if self.fast is True and count == 3:
                break
            count+=1
            if self.fast is True:
                self.addData(newData)
                continue
            if (newData.status).find("대출가능") !=-1:
                newData.isbn = \
                    self.get_isbn(newData.title, newData.href, newData.author, newData.year)
            else:
                newData.isbn = None
            self.addData(newData)

    def get_isbn(self, title, href, author, year):
        isbn = None
        for item in self.sqlResult:
            try:
                if item.book_nm == title and \
                    item.author in author and \
                    ((str(item.publish_year) == year) or (str(year) == "0000")) :
                    isbn = item.isbn
                    break
            except Exception as ex:
                print("에러:", ex)

        if isbn is not None:
            return isbn

        if isbn is None:
            resp = requests.get(href)
            html = ""
            if resp.status_code == 200:
                html = resp.text
            else:
                return 0
            soup = BeautifulSoup(html, 'html.parser')
            soup = soup.find("tbody",{"id":"metaDataBody"})
            soup = soup.find_all("tr")
            for meta_data in soup:
                if meta_data.text.find("ISBN") != -1:
                    isbn = meta_data.find("td",{"class":"detailBody"}).text
                    isbn = self.get_isbn_re(isbn, title, author, year)
                    break
        return isbn
    
    
    def get_book_title(self, soup):
        title = " "
        href = " "
        text = soup.text
        if text is not None:
            title = text
            href = soup.get("href")
        return title, href
    
    def get_book_image(self, soup):
        img = str(soup.get("src"))
        if img.find("noimage") != -1:
            img = "http://cbnul.chungbuk.ac.kr/images/search/bg_book_shadow.png"
        return img
        
    def get_book_info(self, soup):
        author = " "
        publisher = " "
        year = " "
        data = " ".join(str(soup).split())
        #태그로 감싸진 영역 전부지우기
        cleanr = re.compile(r'<.*?>*</.*?>')
        cleantext = " ".join(cleanr.sub(' ', data).split())
        #리스트 변환
        cleantext = cleantext.split('/')
        if len(cleantext) >= 4:
            author = ''.join(cleantext[1])[1:]
            publisher = ''.join(cleantext[2])[1:]
            #올바른 결과인지 확인
            test = publisher.split('.')
            if len(test) >=2:
                publisher = " "
                year = ''.join(test[0])
            else:
                #출판년도와 청구기호 분리하여 출판년도만 저장
                year = cleantext[3].split('.')
                year = ''.join(year[0])[1:]
        publisher = publisher.strip()
        author = author.strip()
        return author, publisher, year
        
    def get_book_call_number(self, soup):
        status = " "
        place = " "
        call_number = " "
        soup = soup.find("p", {"class":"tag"})
        #파싱 형태 : 중앙도서관 [740.76 ㄹ986ㅇ] 대출가능  
        if soup is not None:
            info = " ".join((soup.text).split())
            info = info.split()
            place = info[0]
            status = info[-1]
            call_number = " ".join(info[1:-1])[1:-2]   
        return place, status, call_number