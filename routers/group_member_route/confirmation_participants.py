from fastapi import APIRouter, status, HTTPException, Depends
from mainApp.schemas.group_part_schema import confirmation_part_schema
from mainApp.data.all_database import group_members_models, event_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(prefix="/confirmation_participants", tags=["confirmation_participants"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_participant(request: confirmation_part_schema.ConfirmationParticipant, db: Session = Depends(get_db),
                       authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant_name = request.participant_name
    confirmation = request.confirmation

    actual_confirmation = db.query(event_models.Confirmation). \
        filter(event_models.Confirmation.confirmation_name == confirmation).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not actual_confirmation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid confirmation service", "success": False})

    new_participant = group_members_models.ConfirmationParticipant(participant_name=participant_name,
                                                                   confirmation_id=actual_confirmation.id,
                                                                   confirmation_name=actual_confirmation.
                                                                   confirmation_name)
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    return {"detail": {"message": "Confirmation participant created!", "success": True}}


@router.get("/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=confirmation_part_schema.ReadConfirmationParticipant)
def get_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant = db.query(group_members_models.ConfirmationParticipant). \
        filter(group_members_models.ConfirmationParticipant.confirmation_service_id == int(ind)).all()

    return participant


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant = db.query(group_members_models.ConfirmationParticipant). \
        filter(group_members_models.ConfirmationParticipant.id == int(ind)).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid participant!", "success": False})

    db.delete(participant)
    db.commit()
    return {"detail": {"message": "Confirmation participant deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_participant(ind: str, request: confirmation_part_schema.UpdateConfirmationParticipant,
                       db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant_name = request.participant_name

    participant = db.query(group_members_models.ConfirmationParticipant). \
        filter(group_members_models.ConfirmationParticipant.id == ind).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid participant", "success": False})

    participant.participant_name = participant_name

    db.commit()
    db.refresh(participant)
    return {"detail": {"message": "Confirmation participant updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK)
def get_participant(db: Session = Depends(get_db)):

    participant = db.query(group_members_models.ConfirmationParticipant).all()

    return participant


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK)
def get_participant(ind: str, db: Session = Depends(get_db)):

    participant = db.query(group_members_models.ConfirmationParticipant).\
        filter(group_members_models.ConfirmationParticipant.id == int(ind)).first()

    return participant
