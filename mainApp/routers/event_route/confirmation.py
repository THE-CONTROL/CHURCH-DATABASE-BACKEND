from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.event import confirmation_schema
from mainApp.data.all_database import event_models, group_models, group_members_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from math import ceil

router = APIRouter(prefix="/confirmation", tags=["confirmation"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_confirmation(request: confirmation_schema.Confirmation, db: Session = Depends(get_db),
                        authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    confirmation_name = request.confirmation_name
    confirmation_date = request.confirmation_date
    minister = request.minister

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(confirmation_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Confirmation name must be greater than five characters!",
                                    "success": False})
    for eachConfirmation in actual_congregation.confirmation:
        if eachConfirmation.confirmation_name == confirmation_name:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Confirmation with same name already registered!",
                                        "success": False})
    if len(confirmation_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of confirmation must be given!", "success": False})

    new_confirmation = event_models.Confirmation(confirmation_name=confirmation_name,
                                                 confirmation_date=confirmation_date,
                                                 minister=minister,
                                                 congregation_id=actual_congregation.id,
                                                 congregation_name=actual_congregation.congregation_name)
    db.add(new_confirmation)
    db.commit()
    db.refresh(new_confirmation)
    return {"detail": {"message": "Confirmation created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[confirmation_schema.ReadConfirmation])
def get_confirmations(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    confirmation = db.query(event_models.Confirmation).all()
    return confirmation


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=confirmation_schema.ReadConfirmation)
def get_confirmation(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    confirmation = db.query(event_models.Confirmation).filter(event_models.Confirmation.id == int(ind)).first()

    if not confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid confirmation!", "success": False})

    return confirmation


@router.get("/participant/get/{ind}", status_code=status.HTTP_200_OK)
def get_confirmation_part(ind: str, search: str, page: str = "1", page_size: int = 5,
                          db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    confirmation = db.query(event_models.Confirmation).filter(event_models.Confirmation.id == int(ind)).first()

    if not confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid confirmation!", "success": False})

    participants = confirmation.confirmation_participants
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
def delete_confirmation(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    confirmation = db.query(event_models.Confirmation).filter(event_models.Confirmation.id == int(ind)).first()
    if not confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid confirmation!", "success": False})

    db.delete(confirmation)
    db.commit()
    return {"detail": {"message": "Confirmation deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_confirmation(ind: str, request: confirmation_schema.Confirmation, db: Session = Depends(get_db),
                        authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    confirmation_name = request.confirmation_name
    confirmation_date = request.confirmation_date
    minister = request.minister

    current_admin = authorize.get_jwt_subject()

    confirmation = db.query(event_models.Confirmation).filter(event_models.Confirmation.id == int(ind)).first()
    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()

    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if len(confirmation_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Confirmation name must be greater than five characters!",
                                    "success": False})
    for eachConfirmation in actual_congregation.confirmation:
        if eachConfirmation.confirmation_name == confirmation_name and eachConfirmation != confirmation:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail={"message": "Confirmation with same name already registered!",
                                        "success": False})
    if len(confirmation_date) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date of confirmation must be given!", "success": False})

    members = db.query(group_members_models.ConfirmationParticipant). \
        filter(group_members_models.ConfirmationParticipant.confirmation_name == confirmation.confirmation_name).all()
    if members:
        for member in members:
            member.confirmation_name = confirmation_name

    confirmation.confirmation_name = confirmation_name
    confirmation.confirmation_date = confirmation_date
    confirmation.minister = minister
    confirmation.congregation_name = actual_congregation.congregation_name

    db.commit()
    db.refresh(confirmation)
    return {"detail": {"message": "Confirmation updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK,
            response_model=List[confirmation_schema.ReadConfirmation])
def get_confirmations(db: Session = Depends(get_db)):
    confirmation = db.query(event_models.Confirmation).all()
    return confirmation


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=confirmation_schema.ReadConfirmation)
def get_confirmation(ind: str, db: Session = Depends(get_db)):
    confirmation = db.query(event_models.Confirmation).filter(event_models.Confirmation.id == int(ind)).first()

    if not confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid confirmation!", "success": False})

    return confirmation
