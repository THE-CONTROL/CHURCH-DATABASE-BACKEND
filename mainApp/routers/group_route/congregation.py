from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.group import congregation_schema
from mainApp.data.all_database import group_models, single_models, event_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/congregation", tags=["congregation"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_congregation(request: congregation_schema.Congregation, db: Session = Depends(get_db),
                        authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    congregation_name = request.congregation_name
    location = request.location
    date_setup = request.date_setup
    admin = authorize.get_jwt_subject()
    congregation_head = request.congregation_head
    assistant_congregation_head = request.assistant_congregation_head

    actual_admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == admin).first()

    if len(actual_admin.congregation) > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Only one church is allowed for an admin!", "success": False})
    if not actual_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please give a valid admin!", "success": False})
    if len(congregation_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(congregation_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Church head name must be greater than five characters!",
                                    "success": False})
    if len(assistant_congregation_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": """Assistant church head name must be greater than \
                                               five characters!""", "success": False})
    if len(location) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Location must be given!", "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})

    new_congregation = group_models.Congregation(congregation_name=congregation_name, location=location,
                                                 date_setup=date_setup, admin_id=actual_admin.id,
                                                 congregation_head=congregation_head,
                                                 assistant_congregation_head=assistant_congregation_head,
                                                 admin_name=actual_admin.admin_name)
    db.add(new_congregation)
    db.commit()
    db.refresh(new_congregation)
    return {"detail": {"message": "Church created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[congregation_schema.AllCongregation])
def get_congregations(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    congregations = db.query(group_models.Congregation).all()
    return congregations


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=congregation_schema.AllCongregation)
def get_congregation(ind: int, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    congregation = db.query(group_models.Congregation).filter(group_models.Congregation.id == int(ind)).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    return congregation


@router.get("/members/get/", status_code=status.HTTP_200_OK)
def get_congregation_members(search: str, page: str = "1", page_size: int = 5,
                             db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    members = congregation.members
    search_value = []

    for each in members:
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


@router.get("/elders/get", status_code=status.HTTP_200_OK)
def get_congregation_elders(search: str, page: str = "1", page_size: int = 5,
                            db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    elders = congregation.elders
    search_value = []

    for each in elders:
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


@router.get("/districts/get", status_code=status.HTTP_200_OK)
def get_congregation_districts(search: str, page: str = "1", page_size: int = 5, db: Session = Depends(get_db),
                               authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"message": "Invalid church!", "success": False})

    districts = congregation.districts
    search_value = []

    for each in districts:
        if search in each.district_name:
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


@router.get("/cottages/get", status_code=status.HTTP_200_OK)
def get_congregation_cottages(search: str, page: str = "1", page_size: int = 5,
                              db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    cottages = congregation.cottages
    search_value = []

    for each in cottages:
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


@router.get("/ministries/get", status_code=status.HTTP_200_OK)
def get_congregation_ministries(search: str, page: str = "1", page_size: int = 5,
                                db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    ministries = congregation.ministries
    search_value = []

    for each in ministries:
        if search in each.ministry_name:
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


@router.get("/service/get/", status_code=status.HTTP_200_OK)
def get_congregation_service(search: str, page: str = "1", page_size: int = 5,
                             db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    service = congregation.service
    search_value = []

    for each in service:
        if search in each.service_name:
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


@router.get("/communion_services/get", status_code=status.HTTP_200_OK)
def get_congregation_communion_services(search: str, page: str = "1", page_size: int = 5,
                                        db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()

    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    communion_services = congregation.communion_services
    search_value = []

    for each in communion_services:
        if search in each.service_name:
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


@router.get("/baptism/get", status_code=status.HTTP_200_OK)
def get_congregation_baptism(search: str, page: str = "1", page_size: int = 5,
                             db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()
    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    baptisms = congregation.baptism
    search_value = []

    for each in baptisms:
        if search in each.baptism_name:
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


@router.get("/confirmation/get/", status_code=status.HTTP_200_OK)
def get_congregation_confirmation(search: str, page: str = "1", page_size: int = 5,
                                  db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()
    congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    confirmation = congregation.confirmation
    search_value = []

    for each in confirmation:
        if search in each.confirmation_name:
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


@router.delete("/delete", status_code=status.HTTP_202_ACCEPTED)
def delete_congregation(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    current_admin = authorize.get_jwt_subject()
    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()
    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})

    db.delete(congregation)
    db.commit()
    return {"detail": {"message": "Church deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_congregation(ind: str, request: congregation_schema.Congregation, db: Session = Depends(get_db),
                        authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    congregation_name = request.congregation_name
    location = request.location
    date_setup = request.date_setup
    admin = authorize.get_jwt_subject()
    congregation_head = request.congregation_head
    assistant_congregation_head = request.assistant_congregation_head

    congregation = db.query(group_models.Congregation).filter(group_models.Congregation.id == int(ind)).first()
    actual_admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == admin).first()

    if not congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})
    if len(congregation_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(congregation_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Church head name must be greater than five characters!",
                                    "success": False})
    if len(assistant_congregation_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": """Assistant church head name must be greater than \
                                               five characters!""", "success": False})
    if not actual_admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please give a valid admin!", "success": False})
    if len(location) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Location must be given!", "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})

    districts = db.query(group_models.District). \
        filter(group_models.District.congregation_name == congregation.congregation_name).all()

    cottages = db.query(group_models.Cottage). \
        filter(group_models.Cottage.congregation_name == congregation.congregation_name).all()

    ministries = db.query(group_models.Ministry). \
        filter(group_models.Ministry.congregation_name == congregation.congregation_name).all()

    services = db.query(event_models.Service). \
        filter(event_models.Service.congregation_name == congregation.congregation_name).all()

    baptisms = db.query(event_models.Baptism). \
        filter(event_models.Baptism.congregation_name == congregation.congregation_name).all()

    confirmations = db.query(event_models.Confirmation). \
        filter(event_models.Confirmation.congregation_name == congregation.congregation_name).all()

    communion_services = db.query(event_models.CommunionService). \
        filter(event_models.CommunionService.congregation_name == congregation.congregation_name).all()

    elders = db.query(single_models.Elder). \
        filter(single_models.Elder.congregation_name == congregation.congregation_name).all()

    members = db.query(single_models.Member). \
        filter(single_models.Member.congregation_name == congregation.congregation_name).all()

    if districts:
        for district in districts:
            district.congregation_name = congregation_name
    if cottages:
        for cottage in cottages:
            cottage.congregation_name = congregation_name
    if ministries:
        for ministry in ministries:
            ministry.congregation_name = congregation_name
    if services:
        for services in services:
            services.congregation_name = congregation_name
    if confirmations:
        for confirmation in confirmations:
            confirmation.congregation_name = congregation_name
    if baptisms:
        for baptism in baptisms:
            baptism.congregation_name = congregation_name
    if communion_services:
        for communion_service in communion_services:
            communion_service.congregation_name = congregation_name
    if elders:
        for elder in elders:
            elder.congregation_name = congregation_name
    if members:
        for member in members:
            member.congregation_name = congregation_name

    congregation.congregation_name = congregation_name
    congregation.location = location
    congregation.date_setup = date_setup
    congregation.admin_name = actual_admin.admin_name
    congregation.congregation_head = congregation_head
    congregation.assistant_congregation_head = assistant_congregation_head

    db.commit()
    db.refresh(congregation)
    return {"detail": {"message": "Church updated!", "success": True}}
