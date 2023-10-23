from fastapi import APIRouter, status, HTTPException, Depends
from mainApp.schemas.group_part_schema import communion_part_schema
from mainApp.data.all_database import group_members_models, event_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from typing import List

router = APIRouter(prefix="/communion_participants", tags=["communion_participants"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_participant(request: communion_part_schema.CommunionServiceParticipant, db: Session = Depends(get_db),
                       authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant_name = request.participant_name
    communion_service = request.communion_service
    participant_type = request.participant_type

    actual_communion = db.query(event_models.CommunionService). \
        filter(event_models.CommunionService.service_name == communion_service).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not actual_communion:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid communion service", "success": False})

    new_participant = group_members_models.CommunionServiceParticipant(participant_name=participant_name,
                                                                       participant_type=participant_type,
                                                                       communion_service_id=actual_communion.id,
                                                                       service_name=actual_communion.service_name)
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    return {"detail": {"message": "Communion participant created!", "success": True}}


@router.get("/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=communion_part_schema.ReadCommunionServiceParticipant)
def get_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant = db.query(group_members_models.CommunionServiceParticipant). \
        filter(group_members_models.CommunionServiceParticipant.communion_service_id == int(ind)).all()

    return participant


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant = db.query(group_members_models.CommunionServiceParticipant). \
        filter(group_members_models.CommunionServiceParticipant.id == int(ind)).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid participant!", "success": False})

    db.delete(participant)
    db.commit()
    return {"detail": {"message": "Communion participant deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_participant(ind: str, request: communion_part_schema.UpdateCommunionServiceParticipant,
                       db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant_name = request.participant_name
    participant_type = request.participant_type

    participant = db.query(group_members_models.CommunionServiceParticipant). \
        filter(group_members_models.CommunionServiceParticipant.id == int(ind)).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid participant", "success": False})

    participant.participant_name = participant_name
    participant.participant_type = participant_type

    db.commit()
    db.refresh(participant)
    return {"detail": {"message": "Communion participant updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK,
            response_model=List[communion_part_schema.ReadCommunionServiceParticipant])
def get_participant(db: Session = Depends(get_db)):

    participant = db.query(group_members_models.CommunionServiceParticipant).all()

    return participant


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=communion_part_schema.ReadCommunionServiceParticipant)
def get_participant(ind: str, db: Session = Depends(get_db)):

    participant = db.query(group_members_models.CommunionServiceParticipant). \
        filter(group_members_models.CommunionServiceParticipant.id == int(ind)).first()

    return participant
