from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.Member import Member
from models.BookInfo import BookInfo
from models.Book_MAT import Book_MAT
from models.Location import Location


# 책 정보 조회
def get_books(isbn: str,db:Session):
    return db.query(BookInfo).filter(BookInfo.ISBN == isbn ).first()

def get_locID(isbn: str, db:Session):
    return db.query(Book_MAT).filter(Book_MAT.ISBN == isbn).first()

def get_loc_info(locid: int, db: Session):
    return db.query(Location).filter(Location.LOC_ID == locid).first()


#도서 정보 업데이트
def update_books_info(data: Book_MAT ,db:Session):
    return 0

#보관함 정보 업데이트 (새로운 픽업 데이터 넣기)
