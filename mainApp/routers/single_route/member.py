from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.single import members_schema
from mainApp.data.all_database import single_models, group_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(prefix="/member", tags=["member"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_member(request: members_schema.Member, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    member_name = request.member_name
    sex = request.sex
    marital_status = request.marital_status
    telephone = request.telephone
    baptised = request.baptised
    date_joined = request.date_joined
    district = request.district
    cottage = request.cottage
    discipline = request.discipline
    new_cottage = None

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()
    actual_district = db.query(group_models.District).\
        filter(group_models.District.district_name == district).first()
    actual_cottage = db.query(group_models.Cottage).filter(group_models.Cottage.cottage_name == cottage).first()

    if len(member_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if len(sex) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Sex must be selected!", "success": False})
    if len(marital_status) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Marital status must be given!", "success": False})
    if len(date_joined) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date joined must be given!", "success": False})
    if len(telephone) != 11:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Telephone number must be eleven characters!",
                                    "success": False})
    if not actual_congregation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid congregation", "success": False})
    if not actual_cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid branch", "success": False})
    if not actual_district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid district", "success": False})
    for cottages in actual_district.cottages:
        if cottages.cottage_name == cottage:
            new_cottage = cottages
    if new_cottage is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "District does not contain branch", "success": False})
    if not discipline:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid discipline", "success": False})

    new_member = single_models.Member(member_name=member_name, sex=sex, marital_status=marital_status,
                                      telephone=telephone, baptised=baptised, date_joined=date_joined,
                                      discipline=discipline, congregation_id=actual_congregation.id,
                                      cottage_id=actual_cottage.id, district_id=actual_district.id,
                                      district_name=actual_district.district_name,
                                      cottage_name=actual_cottage.cottage_name)
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return {"detail": {"message": "Member created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[members_schema.ReadMember])
def get_members(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    members = db.query(single_models.Member).all()
    return members


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=members_schema.ReadMember)
def get_member(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    member = db.query(single_models.Member).filter(single_models.Member.id == int(ind)).first()

    if not member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid member!", "success": False})

    return member


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_member(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    member = db.query(single_models.Member).filter(single_models.Member.id == int(ind)).first()
    if not member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid member!", "success": False})

    db.delete(member)
    db.commit()
    return {"detail": {"message": "Member deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_member(ind: str, request: members_schema.UpdateMember, db: Session = Depends(get_db),
                  authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    member_name = request.member_name
    sex = request.sex
    marital_status = request.marital_status
    telephone = request.telephone
    baptised = request.baptised
    date_joined = request.date_joined
    discipline = request.discipline

    member = db.query(single_models.Member).filter(single_models.Member.id == int(ind)).first()

    if len(member_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Member invalid!", "success": False})
    if len(sex) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Sex must be selected!", "success": False})
    if len(marital_status) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Marital status must be given!", "success": False})
    if len(date_joined) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Date joined must be given!", "success": False})
    if len(telephone) != 11:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Telephone number must be eleven characters!",
                                    "success": False})

    member.member_name = member_name
    member.sex = sex
    member.marital_status = marital_status
    member.telephone = telephone
    member.baptised = baptised
    member.date_joined = date_joined
    member.discipline = discipline

    db.commit()
    db.refresh(member)
    return {"detail": {"message": "Member updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK, response_model=List[members_schema.ReadMember])
def get_members(db: Session = Depends(get_db)):

    members = db.query(single_models.Member).all()
    return members


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=members_schema.ReadMember)
def get_member(ind: str, db: Session = Depends(get_db)):

    member = db.query(single_models.Member).filter(single_models.Member.id == int(ind)).first()

    if not member:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid member!", "success": False})

    return member
