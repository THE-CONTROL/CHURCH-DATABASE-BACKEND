from fastapi import APIRouter, status, HTTPException, Depends
from mainApp.schemas.group_part_schema import baptism_part_schema
from mainApp.data.all_database import group_members_models, event_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(prefix="/baptism_participants", tags=["baptism_participants"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_participant(request: baptism_part_schema.BaptismParticipant, db: Session = Depends(get_db),
                       authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant_name = request.participant_name
    baptism = request.baptism

    actual_baptism = db.query(event_models.Baptism).\
        filter(event_models.Baptism.baptism_name == baptism).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not actual_baptism:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid baptism", "success": False})

    new_participant = group_members_models.BaptismParticipant(participant_name=participant_name,
                                                              baptism_id=actual_baptism.id,
                                                              baptism_name=actual_baptism.baptism_name)
    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    return {"detail": {"message": "Baptism participant created!", "success": True}}


@router.get("/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=baptism_part_schema.ReadBaptismParticipant)
def get_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant = db.query(group_members_models.BaptismParticipant).\
        filter(group_members_models.BaptismParticipant.baptism_id == int(ind)).all()

    return participant


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant = db.query(group_members_models.BaptismParticipant).\
        filter(group_members_models.BaptismParticipant.id == int(ind)).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid participant!", "success": False})

    db.delete(participant)
    db.commit()
    return {"detail": {"message": "Baptism participant deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_participant(ind: str, request: baptism_part_schema.UpdateBaptismParticipant,
                       db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    participant_name = request.participant_name

    participant = db.query(group_members_models.BaptismParticipant). \
        filter(group_members_models.BaptismParticipant.id == int(ind)).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid participant", "success": False})

    participant.participant_name = participant_name

    db.commit()
    db.refresh(participant)
    return {"detail": {"message": "Baptism participant updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK)
def get_participant(db: Session = Depends(get_db)):

    participant = db.query(group_members_models.BaptismParticipant).all()

    return participant


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK)
def get_participant(ind: str, db: Session = Depends(get_db)):

    participant = db.query(group_members_models.BaptismParticipant).\
        filter(group_members_models.BaptismParticipant.id == int(ind)).first()

    return participant
