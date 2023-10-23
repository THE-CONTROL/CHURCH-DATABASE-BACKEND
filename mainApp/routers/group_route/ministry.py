from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.group import ministry_schema
from mainApp.data.all_database import group_models, group_members_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/ministry", tags=["ministry"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_ministry(request: ministry_schema.Ministry, db: Session = Depends(get_db),
                    authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    ministry_name = request.ministry_name
    ministry_head = request.ministry_head
    date_setup = request.date_setup
    assistant_ministry_head = request.assistant_ministry_head

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid church!", "success": False})
    for ministry in actual_congregation.ministries:
        if ministry.ministry_name == ministry_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Ministry with same name already registered!",
                                        "success": False})
    if len(ministry_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Ministry name must be greater than two characters!", "success": False})
    if len(ministry_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Ministry head must be greater than five characters!",
                                    "success": False})
    if len(assistant_ministry_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Assistant Ministry head must be greater than five characters!",
                                    "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})

    new_ministry = group_models.Ministry(ministry_name=ministry_name, ministry_head=ministry_head,
                                         date_setup=date_setup, congregation_id=actual_congregation.id,
                                         assistant_ministry_head=assistant_ministry_head,
                                         congregation_name=actual_congregation.congregation_name)
    db.add(new_ministry)
    db.commit()
    db.refresh(new_ministry)
    return {"detail": {"message": "Ministry created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[ministry_schema.ReadMinistry])
def get_ministries(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    ministries = db.query(group_models.Ministry).all()
    return ministries


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=ministry_schema.ReadMinistry)
def get_ministry(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    ministry = db.query(group_models.Ministry).filter(group_models.Ministry.id == int(ind)).first()

    if not ministry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid ministry!", "success": False})

    return ministry


@router.get("/members/get/{ind}", status_code=status.HTTP_200_OK)
def get_ministry_members(ind: str, search: str, page: str = "1", page_size: int = 5,
                         db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    ministry = db.query(group_models.Ministry).filter(group_models.Ministry.id == int(ind)).first()

    if not ministry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid ministry!", "success": False})

    members = ministry.members
    search_value = []

    for each in members:
        if search in each.participant_name:
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
def delete_ministry(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    ministry = db.query(group_models.Ministry).filter(group_models.Ministry.id == int(ind)).first()
    if not ministry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid ministry!", "success": False})

    db.delete(ministry)
    db.commit()
    return {"detail": {"message": "Ministry deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_ministry(ind: str, request: ministry_schema.Ministry, db: Session = Depends(get_db),
                    authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    ministry_name = request.ministry_name
    ministry_head = request.ministry_head
    date_setup = request.date_setup
    assistant_ministry_head = request.assistant_ministry_head

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()
    ministry = db.query(group_models.Ministry).filter(group_models.Ministry.id == int(ind)).first()

    if not ministry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid ministry!", "success": False})
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid church!", "success": False})
    if len(ministry_name) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than two characters!", "success": False})
    if len(ministry_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Ministry must be greater than five characters!",
                                    "success": False})
    if len(assistant_ministry_head) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Assistant Ministry head must be greater than five characters!",
                                    "success": False})
    if len(date_setup) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of creation must be given!", "success": False})
    for eachMinistry in actual_congregation.ministries:
        if eachMinistry.ministry_name == ministry_name and eachMinistry != ministry:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Ministry with same name already registered!",
                                        "success": False})
    members = db.query(group_members_models.MinistryMembers). \
        filter(group_members_models.MinistryMembers.ministry_name == ministry.ministry_name).all()
    if members:
        for member in members:
            member.ministry_name = ministry_name

    ministry.ministry_name = ministry_name
    ministry.ministry_head = ministry_head
    ministry.assistant_ministry_head = assistant_ministry_head
    ministry.date_setup = date_setup
    ministry.congregation_id = actual_congregation.id
    ministry.congregation_name = actual_congregation.congregation_name

    db.commit()
    db.refresh(ministry)
    return {"detail": {"message": "Ministry updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK, response_model=List[ministry_schema.ReadMinistry])
def get_ministries(db: Session = Depends(get_db)):
    ministries = db.query(group_models.Ministry).all()
    return ministries


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=ministry_schema.ReadMinistry)
def get_ministry(ind: str, db: Session = Depends(get_db)):
    ministry = db.query(group_models.Ministry).filter(group_models.Ministry.id == int(ind)).first()

    if not ministry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid ministry!", "success": False})

    return ministry
