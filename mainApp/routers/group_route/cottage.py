from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.group import cottage_schema
from mainApp.data.all_database import group_models, single_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/cottage", tags=["cottage"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_cottage(request: cottage_schema.Cottage, db: Session = Depends(get_db),
                   authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    cottage_name = request.cottage_name
    cottage_address = request.cottage_address
    date_setup = request.date_setup
    district = request.district
    cottage_head = request.cottage_head
    assistant_cottage_head = request.assistant_cottage_head

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()
    actual_district = db.query(group_models.District). \
        filter(group_models.District.district_name == district).first()

    if not actual_district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid district!", "success": False})
    for eachCottage in actual_district.cottages:
        if eachCottage.cottage_name == cottage_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Branch with same name already registered!",
                                        "success": False})
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid church!", "success": False})
    if len(cottage_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(cottage_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Branch head name must be greater than five characters!",
                                    "success": False})
    if len(assistant_cottage_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Assistant branch head name must be greater than five characters!",
                                    "success": False})
    if len(cottage_address) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Branch address must be given!", "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})

    new_cottage = group_models.Cottage(cottage_name=cottage_name, cottage_address=cottage_address,
                                       date_setup=date_setup, congregation_id=actual_congregation.id,
                                       district_id=actual_district.id, cottage_head=cottage_head,
                                       assistant_cottage_head=assistant_cottage_head,
                                       congregation_name=actual_congregation.congregation_name,
                                       district_name=actual_district.district_name)
    db.add(new_cottage)
    db.commit()
    db.refresh(new_cottage)
    return {"detail": {"message": "Branch created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[cottage_schema.ReadCottage])
def get_cottages(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    cottages = db.query(group_models.Cottage).all()

    return cottages


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=cottage_schema.ReadCottage)
def get_cottage(ind: int, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    cottage = db.query(group_models.Cottage).filter(group_models.Cottage.id == int(ind)).first()

    if not cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid branch!", "success": False})

    return cottage


@router.get("/members/get/{ind}", status_code=status.HTTP_200_OK)
def get_cottage_members(ind: str, search: str, page: str = "1", page_size: int = 5,
                        db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    cottage = db.query(group_models.Cottage).filter(group_models.Cottage.id == int(ind)).first()

    if not cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid branch!", "success": False})

    cottage_members = cottage.members

    search_value = []

    for each in cottage_members:
        if search in each.member_name:
            search_value.append(each)

    page = int(page)
    start = (page - 1) * page_size
    if len(search_value) > start + page_size:
        end = start + page_size
    else:
        end = len(search_value)
    pages = ceil((len(search_value) / page_size))
    if page - 1 > 0:
        prev_page = page - 1
    else:
        prev_page = None
    if page + 1 > pages:
        next_page = None
    else:
        next_page = page + 1

    return {"data": search_value[start:end], "meta": {"page": page, "next_page": next_page,
                                                      "prev_page": prev_page, "pages": pages,
                                                      "num_items": len(search_value),
                                                      "last_item": end}}


@router.get("/elders/get/{ind}", status_code=status.HTTP_200_OK)
def get_cottage_elders(ind: str, search: str, page: str = "1", page_size: int = 5,
                       db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    cottage = db.query(group_models.Cottage).filter(group_models.Cottage.id == int(ind)).first()

    if not cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid branch!", "success": False})

    cottage_elders = cottage.elders

    search_value = []

    for each in cottage_elders:
        if search in each.elder_name:
            search_value.append(each)

    page = int(page)
    start = (page - 1) * page_size
    if len(search_value) > start + page_size:
        end = start + page_size
    else:
        end = len(search_value)
    pages = ceil((len(search_value) / page_size))
    if page - 1 > 0:
        prev_page = page - 1
    else:
        prev_page = None
    if page + 1 > pages:
        next_page = None
    else:
        next_page = page + 1

    return {"data": search_value[start:end], "meta": {"page": page, "next_page": next_page,
                                                      "prev_page": prev_page, "pages": pages,
                                                      "num_items": len(search_value),
                                                      "last_item": end}}


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_cottage(ind: int, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    cottage = db.query(group_models.Cottage).filter(group_models.Cottage.id == int(ind)).first()
    if not cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid branch!", "success": False})

    db.delete(cottage)
    db.commit()
    return {"detail": {"message": "Branch deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_cottage(ind: int, request: cottage_schema.UpdateCottage, db: Session = Depends(get_db),
                   authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    cottage_name = request.cottage_name
    cottage_address = request.cottage_address
    date_setup = request.date_setup
    cottage_head = request.cottage_head
    assistant_cottage_head = request.assistant_cottage_head

    current_admin = authorize.get_jwt_subject()

    cottage = db.query(group_models.Cottage).filter(group_models.Cottage.id == int(ind)).first()
    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid branch!", "success": False})
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})
    actual_district = db.query(group_models.District). \
        filter(group_models.District.id == cottage.district_id).first()
    if not actual_district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})
    if len(cottage_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(cottage_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Branch head name must be greater than five characters!",
                                    "success": False})
    if len(assistant_cottage_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Assistant branch head name must be greater than five characters!",
                                    "success": False})
    if len(cottage_address) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Branch address must be given!", "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})
    for eachCottage in actual_district.cottages:
        if eachCottage.cottage_name == cottage_name and eachCottage != cottage:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Branch with same name already registered!",
                                        "success": False})

    elders = db.query(single_models.Elder). \
        filter(single_models.Elder.cottage_name == cottage.cottage_name).all()

    members = db.query(single_models.Member). \
        filter(single_models.Member.cottage_name == cottage.cottage_name).all()

    if elders:
        for elder in elders:
            elder.cottage_name = cottage_name
    if members:
        for member in members:
            member.cottage_name = cottage_name

    cottage.cottage_name = cottage_name
    cottage.cottage_address = cottage_address
    cottage.date_setup = date_setup
    cottage.cottage_head = cottage_head
    cottage.assistant_cottage_head = assistant_cottage_head

    db.commit()
    db.refresh(cottage)
    return {"detail": {"message": "Branch updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK, response_model=List[cottage_schema.ReadCottage])
def get_special_cottages(db: Session = Depends(get_db)):
    cottages = db.query(group_models.Cottage).all()
    return cottages


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=cottage_schema.ReadCottage)
def get_special_cottage(ind: int, db: Session = Depends(get_db)):
    cottage = db.query(group_models.Cottage).filter(group_models.Cottage.id == int(ind)).first()

    if not cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid branch!", "success": False})

    return cottage
