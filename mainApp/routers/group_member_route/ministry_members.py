from fastapi import APIRouter, status, HTTPException, Depends
from mainApp.schemas.group_part_schema import ministry_part_schema
from mainApp.data.all_database import group_members_models, group_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(prefix="/ministry_members", tags=["ministry_members"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_participant(request: ministry_part_schema.MinistryMembers, db: Session = Depends(get_db),
                       authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    participant_name = request.participant_name
    ministry = request.ministry
    date_joined = request.date_joined

    actual_ministry = db.query(group_models.Ministry). \
        filter(group_models.Ministry.ministry_name == ministry).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not actual_ministry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid confirmation service", "success": False})
    if len(date_joined) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter the date joined!", "success": False})

    new_participant = group_members_models.MinistryMembers(participant_name=participant_name,
                                                           date_joined=date_joined, ministry_id=actual_ministry.id,
                                                           ministry_name=actual_ministry.ministry_name)

    db.add(new_participant)
    db.commit()
    db.refresh(new_participant)
    return {"detail": {"message": "Ministry member created!", "success": True}}


@router.get("/get/{ind}", status_code=status.HTTP_200_OK,
            response_model=ministry_part_schema.ReadMinistryMembers)
def get_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    participant = db.query(group_members_models.MinistryMembers). \
        filter(group_members_models.MinistryMembers.ministry_id == int(ind)).all()

    return participant


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_participant(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    participant = db.query(group_members_models.MinistryMembers). \
        filter(group_members_models.MinistryMembers.id == int(ind)).first()
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid participant!", "success": False})

    db.delete(participant)
    db.commit()
    return {"detail": {"message": "Ministry member deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_participant(ind: str, request: ministry_part_schema.UpdateMinistryMembers,
                       db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})
    participant_name = request.participant_name
    date_joined = request.date_joined

    participant = db.query(group_members_models.MinistryMembers). \
        filter(group_members_models.MinistryMembers.id == int(ind)).first()

    if len(participant_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not participant:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid participant", "success": False})

    participant.participant_name = participant_name
    participant.date_joined = date_joined

    db.commit()
    db.refresh(participant)
    return {"detail": {"message": "Ministry member updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK)
def get_participant(db: Session = Depends(get_db)):
    participants = db.query(group_members_models.MinistryMembers).all()

    return participants


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK)
def get_participant(ind: str, db: Session = Depends(get_db)):
    participant = db.query(group_members_models.MinistryMembers). \
        filter(group_members_models.MinistryMembers.id == int(ind)).first()

    return participant
