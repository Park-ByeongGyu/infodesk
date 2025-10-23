from fastapi import APIRouter, HTTPException, status, Depends, Query
from database import SessionLocal
from sqlalchemy.orm import Session
from schemas.informationDesk import *
from crud import infodeskCRUD
from datetime import date, timedelta
from models.Rental import Rental

router = APIRouter(prefix="/infodesk", tags=["Infodesk"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#회원 인증
@router.post("/auth", response_model=AuthenticationResult)
def authenticate(auth: Authentication, db: Session = Depends(get_db)):
    member = infodeskCRUD.get_member_by_cardnumber(db, auth.cardNumber)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="유효하지 않은 회원 카드입니다."
        )
    
    return AuthenticationResult(
        memberID=str(member.MemberID),
        name=member.Name,
        memberType=member.MemberType.value
    )

#도서 조회
@router.get("/books", response_model=BookSearch)
def get_bookInfo(
    keyword: str = Query(None, description="검색 키워드"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    per_page: int = Query(5, ge=1, le=30, description="페이지당 데이터 수"),
    db: Session = Depends(get_db)
):
    total, books = infodeskCRUD.get_books(db, keyword, page, per_page)
    print("hello")
    #도서 대여 가능 여부
    #Rental의 ReturnDate - DueDate로 대여 여부 결정

    copyids = []
    for book in books:  #ISBN을 통해 도서관 보유 책 회
        bookmats = infodeskCRUD.get_book_status(db, book.ISBN)
        for bookmat in bookmats:
            copyids.append(bookmat.CopyID)

    rentalStatus = LoanStatus.UNAVAILABLE
    results = []
    rental = infodeskCRUD.get_rental_status(db, copyids)
    for returnDate in rental:
        print(returnDate + "ddddddddddd")
        if returnDate is None:
            rentalStatus = LoanStatus.AVAILABLE
        else:
            rentalStatus = LoanStatus.UNAVAILABLE

        for book in books:
            BookInfo(
            isbn=book.ISBN,
            title=book.Title,
            author=book.Author,
            publisher=book.Publisher,
            status=rentalStatus
        )
        results.append(BookInfo)

    return BookSearch(
        total=total,
        page=page,
        perPage=per_page,
        result=results
    )

#도서 조회 후 위치 보기
@router.get("/books/{isbn}", response_model=BookLocation)
def get_book_location(isbn: str, db:Session = Depends(get_db)):
    #db에서 isbn을 조회후  위치 정보를 전송
    loc = infodeskCRUD.get_book_location(db, isbn)
    if not loc:
        raise HTTPException(status_code=404, detail="해당 바코드의 도서를 찾을 수 없습니다.")
    if  not loc:
        return BookLocation(
            locationName="",
            locType="",
            zoneName="",
            floor="",
            message="해당 도서는 현재 없습니다. 안내 데스크에 문의바랍니다."
        )
    return BookLocation(
        locationName=loc.LocationName,
        locType=loc.LOC_TY,
        zoneName=loc.ZoneName,
        floor=loc.Floor
    )

# 도서 직접 대출
@router.post("/books/direct", response_model=Loan)
def create_directLoan(
    memberID : str,
    barcode : str,
    db : Session = Depends(get_db)):
    bookMat = infodeskCRUD.get_copy_book(db, barcode)

    if not bookMat.Barcode:
        raise HTTPException(status_code=404, detail="해당 바코드의 도서를 찾을 수 없습니다.")
    
    copyid = bookMat.CopyID
    memberid = int(memberID)
    loan_date = date.today()
    due_date = loan_date + timedelta(days=14)
    return_date = None
    extension_count = 0
    late_fee = 0

    rentalDate = Rental(
        CopyID = copyid,
        MemberID = memberid,
        LoanDate = loan_date,
        DueDate = due_date,
        ReturnDate = return_date,
        ExtensionCount = extension_count,
        LateFee = late_fee
    )

    infodeskCRUD.create_rental(db, rentalDate)
   
    return Loan(
        loanDate=loan_date,
        dueDate=due_date
    )



# 도서 픽업 대출
@router.post("/books/pickup", response_model=Loan)
def create_pickupLoan(
    memberID : str,
    barcode : str,
    locname : str,
    db : Session = Depends(get_db)):
    try:

        member = infodeskCRUD.get_member_info(db, memberID)

        if not member.MemberID:
            raise HTTPException(status_code=400, detail="해당 회원은 존재하지 않습니다.")

        bookMat = infodeskCRUD.get_copy_book(db, barcode)

        if not bookMat.Barcode:
            raise HTTPException(status_code=404, detail="해당 바코드의 도서를 찾을 수 없습니다.")
        
        location = infodeskCRUD.get_box_status(db, locname)

        if location.CurrentStatus == "불가가능":
            raise HTTPException(status_code=400, detail="해당 위치는 현재 이용할 수 없습니다.")
        
        

        copyid = bookMat.CopyID
        memberid = int(memberID)
        loan_date = date.today()
        due_date = loan_date + timedelta(days=14)
        return_date = None
        extension_count = 0
        late_fee = 0

        rentalDate = Rental(
            CopyID = copyid,
            MemberID = memberid,
            LoanDate = loan_date,
            DueDate = due_date,
            ReturnDate = return_date,
            ExtensionCount = extension_count,
            LateFee = late_fee
        )

        infodeskCRUD.create_rental(db, rentalDate)

        return Loan(
            loanDate=loan_date,
            dueDate=due_date,
            locationName=location.LocationName
            #preparationTime=, 이 부분은 아직 보류
        )
            
        
    except HTTPException as e:
        return {"error":e.detail}
    
   
    
