from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.event import communion_service_schema
from mainApp.data.all_database import event_models, group_models, group_members_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/communion_service", tags=["communion_service"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_communion_service(request: communion_service_schema.CommunionService, db: Session = Depends(get_db),
                             authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service_name = request.service_name
    service_date = request.service_date
    service_head_count = request.service_head_count

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(service_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Communion service name must be greater than five characters!",
                                    "success": False})
    for eachCommunionService in actual_congregation.communion_services:
        if eachCommunionService.service_name == service_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Communion service with same name already registered!",
                                        "success": False})
    if len(service_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of communion service must be given!", "success": False})

    new_communion_service = event_models.CommunionService(service_name=service_name, service_date=service_date,
                                                          service_head_count=service_head_count,
                                                          congregation_id=actual_congregation.id,
                                                          congregation_name=actual_congregation.congregation_name)
    db.add(new_communion_service)
    db.commit()
    db.refresh(new_communion_service)
    return {"detail": {"message": "Communion service created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK,
            response_model=List[communion_service_schema.ReadCommunionService])
def get_communion_services(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    communion_service = db.query(event_models.CommunionService).all()
    return communion_service


@router.get("/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=communion_service_schema.ReadCommunionService)
def get_communion_service(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    communion_service = db.query(event_models.CommunionService).\
        filter(event_models.CommunionService.id == int(ind)).first()

    if not communion_service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid communion service!", "success": False})

    return communion_service


@router.get("/participant/get/{ind}", status_code=status.HTTP_200_OK)
def get_communion_service_part(ind: str, search: str, page: str = "1", page_size: int = 5,
                               db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    communion_service = db.query(event_models.CommunionService).\
        filter(event_models.CommunionService.id == int(ind)).first()

    if not communion_service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid communion service!", "success": False})

    participants = communion_service.participants
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
def delete_communion_service(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    communion_service = db.query(event_models.CommunionService).\
        filter(event_models.CommunionService.id == int(ind)).first()
    if not communion_service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid communion service!", "success": False})

    db.delete(communion_service)
    db.commit()
    return {"detail": {"message": "Communion service deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_communion_service(ind: str, request: communion_service_schema.CommunionService,
                             db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service_name = request.service_name
    service_date = request.service_date
    service_head_count = request.service_head_count

    current_admin = authorize.get_jwt_subject()

    communion_service = db.query(event_models.CommunionService).\
        filter(event_models.CommunionService.id == int(ind)).first()
    actual_congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(service_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Communion service name must be greater than five characters!",
                                    "success": False})
    for eachCommunionService in actual_congregation.communion_services:
        if eachCommunionService.service_name == service_name and eachCommunionService != communion_service:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Communion service with same name already registered!",
                                        "success": False})
    if len(service_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of communion service must be given!", "success": False})

    members = db.query(group_members_models.CommunionServiceParticipant). \
        filter(group_members_models.CommunionServiceParticipant.service_name == communion_service.service_name).all()
    if members:
        for member in members:
            member.service_name = service_name

    communion_service.service_name = service_name
    communion_service.service_date = service_date
    communion_service.service_head_count = service_head_count

    db.commit()
    db.refresh(communion_service)
    return {"detail": {"message": "Communion service updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK,
            response_model=List[communion_service_schema.ReadCommunionService])
def get_communion_services(db: Session = Depends(get_db)):
    communion_service = db.query(event_models.CommunionService).all()
    return communion_service


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=communion_service_schema.ReadCommunionService)
def get_communion_service(ind: str, db: Session = Depends(get_db)):
    communion_service = db.query(event_models.CommunionService).\
        filter(event_models.CommunionService.id == int(ind)).first()

    if not communion_service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid communion service!", "success": False})

    return communion_service
