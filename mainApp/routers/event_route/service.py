from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.event import service_schema
from mainApp.data.all_database import event_models, group_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(prefix="/service", tags=["service"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_service(request: service_schema.Service, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service_name = request.service_name
    service_date = request.service_date
    description = request.description
    service_type = request.service_type
    no_men = request.no_men
    no_women = request.no_women
    no_children = request.no_children
    no_visitors = request.no_visitors
    head_minister = request.head_minister
    assistant_minister = request.assistant_minister
    time_period = request.time_period

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(service_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Service name must be greater than five characters!",
                                    "success": False})
    for eachService in actual_congregation.service:
        if eachService.service_name == service_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Service with same name already registered!",
                                        "success": False})
    if len(head_minister) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Head minister name must be greater than two characters!",
                                    "success": False})
    if len(service_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of service must be given!", "success": False})

    new_service = event_models.Service(service_name=service_name, head_minister=head_minister,
                                       assistant_minister=assistant_minister, service_date=service_date,
                                       service_type=service_type, description=description, no_men=no_men,
                                       no_women=no_women, no_children=no_children,
                                       no_visitors=no_visitors, time_period=time_period,
                                       congregation_id=actual_congregation.id,
                                       congregation_name=actual_congregation.congregation_name)
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return {"detail": {"message": "Service created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[service_schema.ReadService])
def get_service(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service = db.query(event_models.Service).all()
    return service


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=service_schema.ReadService)
def get_service(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service = db.query(event_models.Service).filter(event_models.Service.id == int(ind)).first()

    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid service!", "success": False})

    return service


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_service(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service = db.query(event_models.Service).filter(event_models.Service.id == int(ind)).first()
    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid service!", "success": False})

    db.delete(service)
    db.commit()
    return {"detail": {"message": "Service deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_service(ind: str, request: service_schema.Service, db: Session = Depends(get_db),
                   authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    service_name = request.service_name
    service_date = request.service_date
    description = request.description
    service_type = request.service_type
    no_men = request.no_men
    no_women = request.no_women
    no_children = request.no_children
    no_visitors = request.no_visitors
    head_minister = request.head_minister
    assistant_minister = request.assistant_minister
    time_period = request.time_period

    current_admin = authorize.get_jwt_subject()

    service = db.query(event_models.Service).filter(event_models.Service.id == int(ind)).first()
    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid service!", "success": False})
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(service_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Service name must be greater than five characters!",
                                    "success": False})
    for eachService in actual_congregation.service:
        if eachService.service_name == service_name and eachService != service:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Service with same name already registered!",
                                        "success": False})
    if len(head_minister) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Head minister name must be greater than two characters!",
                                    "success": False})
    if len(service_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of service must be given!", "success": False})

    service.service_name = service_name
    service.service_date = service_date
    service.description = description
    service.service_type = service_type
    service.no_men = no_men
    service.no_women = no_women
    service.no_children = no_children
    service.no_visitors = no_visitors
    service.head_minister = head_minister
    service.assistant_minister = assistant_minister
    service.time_period = time_period

    db.commit()
    db.refresh(service)
    return {"detail": {"message": "Service updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK, response_model=List[service_schema.ReadService])
def get_service(db: Session = Depends(get_db)):
    service = db.query(event_models.Service).all()
    return service


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=service_schema.ReadService)
def get_service(ind: str, db: Session = Depends(get_db)):
    service = db.query(event_models.Service).filter(event_models.Service.id == int(ind)).first()

    if not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid service!", "success": False})

    return service
