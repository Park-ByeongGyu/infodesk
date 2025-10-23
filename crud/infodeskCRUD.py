from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.Member import Member
from models.BookInfo import BookInfo
from models.Book_MAT import Book_MAT
from models.Location import Location
from models.Rental import Rental
from typing import List

#회원 인증 
def get_member_by_cardnumber(db: Session, cardnumber: str):
    return db.query(Member).filter(Member.CardNumber == cardnumber).first()


#도서 조회
def get_books(db: Session, keyword: str = None, page: int = 1, per_page: int = 5):
    query = db.query(BookInfo)

    if keyword:
        search = f"%{keyword}%"
        query = query.filter(
            or_(
                BookInfo.Title.like(search),
                BookInfo.Author.like(search),
                BookInfo.Publisher.like(search),
            )
        )
    total = query.count()
    books = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return total, books

def get_book_status(db: Session, isbn: str): #북 상태 조회를 위한 도서관 보유 책 조회
    book_mat = db.query(Book_MAT).filter(Book_MAT.ISBN == isbn).all()
    if not book_mat:
        raise HTTPException(status_code=404, detail=f"도서 ISBN {isbn}가 없습니다.")
    return book_mat

def get_rental_status(db: Session, copyids: List):
    rentals = []
    for copyid in copyids:
        records = db.query(Rental.ReturnDate).filter(Rental.CopyID == copyid).all()
        rentals.append(records)
    return rentals # 튜플(duedate, retrundate)형식의 리스트 값

#도서 조회 후 위치 보기

def get_book_location(db: Session, isbn: str):
    locID = db.query(Book_MAT).filter(Book_MAT.ISBN == isbn).first()
    if locID is None:
        raise HTTPException(status_code=404, detail=f"도서 ISBN {isbn}가 없습니다.")

    location = db.query(Location).filter(Location.LOC_ID == locID.LOC_ID).first()
    if location is None:
        raise HTTPException(status_code=404, detail=f"해당 도서는 현재 보유하고 있지 않습니다.")

    return location


#도서 직접 및 픽업 대출

def get_copy_book(db:Session, barcode: str):
    return db.query(Book_MAT).filter(Book_MAT.Barcode == barcode).first()

def create_rental(db:Session, db_rantal: Rental):
    db.add(db_rantal)
    db.commit()
    db.refresh(db_rantal)
    return db_rantal

#픽업대 상태 조회
def get_box_status(db: Session, loc_name: str):
    return db.query(Location).filter(Location.LocationName == loc_name).first()

#회원 정보 확인용
def get_member_info(db:Session, member_id: str):
    return db.query(Member).filter(Member.MemberID == member_id).first()