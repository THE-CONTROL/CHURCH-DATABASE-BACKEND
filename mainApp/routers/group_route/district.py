from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.group import district_schema
from mainApp.data.all_database import group_models, single_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/district", tags=["district"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_district(request: district_schema.District, db: Session = Depends(get_db),
                    authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()
    district_name = request.district_name
    coverage_area = request.coverage_area
    date_setup = request.date_setup
    district_head = request.district_head
    assistant_district_head = request.assistant_district_head

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid church!", "success": False})
    for district in actual_congregation.districts:
        if district.district_name == district_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "District with same name already registered!",
                                        "success": False})
    if len(district_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(district_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "District head name must be greater than five characters!",
                                    "success": False})
    if len(assistant_district_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Assistant district head name must be greater than five characters!",
                                    "success": False})
    if len(coverage_area) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Coverage area must be given!", "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})

    new_district = group_models.District(district_name=district_name, coverage_area=coverage_area,
                                         date_setup=date_setup, congregation_id=actual_congregation.id,
                                         assistant_district_head=assistant_district_head,
                                         district_head=district_head,
                                         congregation_name=actual_congregation.congregation_name)
    db.add(new_district)
    db.commit()
    db.refresh(new_district)
    return {"detail": {"message": "District created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[district_schema.ReadDistrict])
def get_districts(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    districts = db.query(group_models.District).all()

    return districts


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=district_schema.ReadDistrict)
def get_district(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()

    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})

    return district


@router.get("/members/get/{ind}", status_code=status.HTTP_200_OK)
def get_district_members(ind: str, search: str, page: str = "1", page_size: int = 5,
                         db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()

    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})

    district_members = district.members

    search_value = []

    for each in district_members:
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
def get_district_elders(ind: str, search: str, page: str = "1", page_size: int = 5,
                        db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()

    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})

    district_elders = district.elders

    search_value = []

    for each in district_elders:
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


@router.get("/cottages/get/{ind}", status_code=status.HTTP_200_OK)
def get_district_cottages(ind: str, search: str, page: str = "1", page_size: int = 5,
                          db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()

    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})

    district_cottages = district.cottages

    search_value = []

    for each in district_cottages:
        if search in each.cottage_name:
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
def delete_district(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()
    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})

    db.delete(district)
    db.commit()
    return {"detail": {"message": "District deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_district(ind: str, request: district_schema.District, db: Session = Depends(get_db),
                    authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()
    district_name = request.district_name
    coverage_area = request.coverage_area
    date_setup = request.date_setup
    district_head = request.district_head
    assistant_district_head = request.assistant_district_head

    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()
    actual_congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})
    if len(district_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(district_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "District head name must be greater than five characters!",
                                    "success": False})
    if len(assistant_district_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Assistant district head name must be greater than five characters!",
                                    "success": False})
    if len(coverage_area) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Coverage area must be given!", "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})
    for eachDistrict in actual_congregation.districts:
        if eachDistrict.district_name == district_name and eachDistrict != district:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "District with same name already registered!",
                                        "success": False})

    cottages = db.query(group_models.Cottage). \
        filter(group_models.Cottage.district_name == district.district_name).all()

    elders = db.query(single_models.Elder). \
        filter(single_models.Elder.district_name == district.district_name).all()

    members = db.query(single_models.Member). \
        filter(single_models.Member.district_name == district.district_name).all()

    if cottages:
        for cottage in cottages:
            cottage.district_name = district_name
    if elders:
        for elder in elders:
            elder.district_name = district_name
    if members:
        for member in members:
            member.district_name = district_name

    district.district_name = district_name
    district.coverage_area = coverage_area
    district.date_setup = date_setup
    district.district_head = district_head
    district.assistant_district_head = assistant_district_head

    db.commit()
    db.refresh(district)
    return {"detail": {"message": "District updated!", "success": True}}


@router.get("/special/get/", status_code=status.HTTP_200_OK, response_model=List[district_schema.ReadDistrict])
def get_special_districts(db: Session = Depends(get_db)):
    districts = db.query(group_models.District).all()
    return districts


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=district_schema.ReadDistrict)
def get_special_district(ind: str, db: Session = Depends(get_db)):
    district = db.query(group_models.District).filter(group_models.District.id == int(ind)).first()

    if not district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid district!", "success": False})

    return district
