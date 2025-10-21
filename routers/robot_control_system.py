from fastapi import APIRouter, Depends, Query,HTTPException
from schemas.robot_control_system import *
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import robot_control_system_CURD
from models.Location import Location

router = APIRouter(prefix="/app", tags=["robot"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 도서 정보 요청
@router.get("/books/{ISBN}", response_model=BooksInfoResponse)
def get_books_info(ISBN: str, db: Session = Depends(get_db)):
    # 책 조회
    books = robot_control_system_CURD.get_books(ISBN, db)
    if not books:
        raise HTTPException(status_code=404, detail=f"ISBN {ISBN}의 도서를 찾을 수 없습니다.")

    # LOC_ID 조회
    book_mat = robot_control_system_CURD.get_locID(ISBN, db)
    if not book_mat or not book_mat.LOC_ID:
        raise HTTPException(status_code=404, detail=f"ISBN {ISBN}에 대한 위치 정보가 없습니다.")

    locid = book_mat.LOC_ID

    # Location 정보 조회
    location_info = robot_control_system_CURD.get_loc_info(locid, db)
    if not location_info:
        raise HTTPException(status_code=404, detail=f"LOC_ID {locid}에 대한 위치 정보가 없습니다.")

    # Pydantic 모델 매핑
    _bookinfo_list = [
        BookInfo(
            title=books.Title,
            author=books.Author,
            publisher=books.Publisher
        )
    ]

    _location = Loc(
        locationName=location_info.LocationName,
        locType=location_info.LOC_TY,
        zoneName=location_info.ZoneName,
        coordinateX=location_info.CoordinateX,
        coordinateY=location_info.CoordinateY
    )

    return BooksInfoResponse(
        bookInfo=_bookinfo_list,
        location=_location
    )


    



# 도서 정보 업데이트



# 보관함 정보 업데이트
