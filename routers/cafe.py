from fastapi import APIRouter, HTTPException, Request, Depends, Query
from typing import List
from schemas.cafe import Order, OrderList,BeverageList, BeverageSearch
from sqlalchemy.orm import Session
from database import SessionLocal
from crud import cafeCURD
from models.BeverageOrder import BeverageOrder

router = APIRouter(prefix="/cafe", tags=["Cafe Orders"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 주문 생성
@router.post("/order", response_model=OrderList)
def create_order(order: Order, db: Session = Depends(get_db)):
   try:
       
        member_id = 6
        total_amount = order.totalAmount
        payment_info = order.paymentInfo
        order_status = order.orderStatus
        
        beverage = BeverageOrder(
                MemberID = member_id,
                TotalAmount = total_amount,
                PaymentInfo = payment_info,
                OrderStatus = order_status
        )
        cafeCURD.create_order(db, beverage)
       
        beverageorder = cafeCURD.get_beverageOrder(db)
   
        return OrderList(
            orderID= beverageorder.OrderID,
            orderStatus= beverageorder.OrderStatus
        )
   except HTTPException as e:
       return {"error":e.detail}


#메뉴 조회
@router.get("/menu", response_model=BeverageList)
def getMenu(db: Session = Depends(get_db)):
    menus = cafeCURD.get_menu(db)
    menulist = []
    for menu in menus:
        menu_info = BeverageSearch(
            beverageName = menu.BeverageName,
            price= menu.Price,
            description= menu.Description,
            stockStatus= menu.StockStatus
        )
        menulist.append(menu_info)
    return BeverageList(
        beverage= menulist
    )





