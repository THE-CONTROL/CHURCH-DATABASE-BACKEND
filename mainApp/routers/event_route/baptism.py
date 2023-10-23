from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.event import baptism_schema
from mainApp.data.all_database import event_models, group_models, group_members_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/baptism", tags=["baptism"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_baptism(request: baptism_schema.Baptism, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    baptism_name = request.baptism_name
    baptism_date = request.baptism_date
    minister = request.minister

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(baptism_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Baptism name must be greater than five characters!",
                                    "success": False})
    for eachBaptism in actual_congregation.baptism:
        if eachBaptism.baptism_name == baptism_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Baptism with same name already registered!",
                                        "success": False})
    if len(baptism_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of baptism must be given!", "success": False})

    new_baptism = event_models.Baptism(baptism_name=baptism_name, baptism_date=baptism_date,
                                       minister=minister,
                                       congregation_id=actual_congregation.id,
                                       congregation_name=actual_congregation.congregation_name)
    db.add(new_baptism)
    db.commit()
    db.refresh(new_baptism)
    return {"detail": {"message": "Baptism created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[baptism_schema.ReadBaptism])
def get_baptisms(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    baptism = db.query(event_models.Baptism).all()
    return baptism


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=baptism_schema.ReadBaptism)
def get_baptism(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    baptism = db.query(event_models.Baptism).filter(event_models.Baptism.id == int(ind)).first()

    if not baptism:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid baptism!", "success": False})

    return baptism


@router.get("/participant/get/{ind}", status_code=status.HTTP_200_OK)
def get_baptism_part(ind: str, search: str, page: str = "1", page_size: int = 5,
                     db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    baptism = db.query(event_models.Baptism).filter(event_models.Baptism.id == int(ind)).first()

    if not baptism:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid baptism!", "success": False})

    participants = baptism.baptism_participants
    search_value = []

    for each in participants:
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
def delete_baptism(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    baptism = db.query(event_models.Baptism).filter(event_models.Baptism.id == int(ind)).first()
    if not baptism:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid baptism!", "success": False})

    db.delete(baptism)
    db.commit()
    return {"detail": {"message": "Baptism deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_baptism(ind: str, request: baptism_schema.Baptism, db: Session = Depends(get_db),
                   authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    baptism_name = request.baptism_name
    baptism_date = request.baptism_date
    minister = request.minister

    current_admin = authorize.get_jwt_subject()

    baptism = db.query(event_models.Baptism).filter(event_models.Baptism.id == int(ind)).first()
    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(baptism_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Baptism name must be greater than five characters!",
                                    "success": False})
    for eachBaptism in actual_congregation.baptism:
        if eachBaptism.baptism_name == baptism_name and eachBaptism != baptism:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Baptism with same name already registered!",
                                        "success": False})
    if len(baptism_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of baptism must be given!", "success": False})

    members = db.query(group_members_models.BaptismParticipant). \
        filter(group_members_models.BaptismParticipant.baptism_name == baptism.baptism_name).all()
    if members:
        for member in members:
            member.baptism_name = baptism_name

    baptism.baptism_name = baptism_name
    baptism.baptism_date = baptism_date
    baptism.minister = minister

    db.commit()
    db.refresh(baptism)
    return {"detail": {"message": "Baptism updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK, response_model=List[baptism_schema.ReadBaptism])
def get_baptisms(db: Session = Depends(get_db)):
    baptism = db.query(event_models.Baptism).all()
    return baptism


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=baptism_schema.ReadBaptism)
def get_baptism(ind: str, db: Session = Depends(get_db)):
    baptism = db.query(event_models.Baptism).filter(event_models.Baptism.id == int(ind)).first()

    if not baptism:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid baptism!", "success": False})

    return baptism
