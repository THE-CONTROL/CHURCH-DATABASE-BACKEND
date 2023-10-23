from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from mainApp.schemas.single import elder_schema
from mainApp.data.all_database import single_models, group_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

router = APIRouter(prefix="/elder", tags=["elder"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def create_elder(request: elder_schema.Elder, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    elder_name = request.elder_name
    sex = request.sex
    marital_status = request.marital_status
    telephone = request.telephone
    elder_type = request.elder_type
    date_joined = request.date_joined
    district = request.district
    cottage = request.cottage
    elder_post = request.elder_post
    new_cottage = None

    current_admin = authorize.get_jwt_subject()

    actual_congregation = db.query(group_models.Congregation). \
        filter(group_models.Congregation.admin_name == current_admin).first()
    actual_district = db.query(group_models.District).\
        filter(group_models.District.district_name == district).first()
    actual_cottage = db.query(group_models.Cottage).filter(group_models.Cottage.cottage_name == cottage).first()

    if len(elder_name) < 5:
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
                            detail={"message": "Please enter a valid congregation!", "success": False})
    if not actual_cottage:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid branch!", "success": False})
    if not actual_district:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid district", "success": False})
    for cottages in actual_district.cottages:
        if cottages.cottage_name == cottage:
            new_cottage = cottages
    if new_cottage is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "District does not contain branch", "success": False})
    if len(elder_post) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid elder position", "success": False})

    new_elder = single_models.Elder(elder_name=elder_name, sex=sex, marital_status=marital_status,
                                    telephone=telephone, date_joined=date_joined, elder_post=elder_post,
                                    elder_type=elder_type, congregation_id=actual_congregation.id,
                                    cottage_id=actual_cottage.id, district_id=actual_district.id,
                                    district_name=actual_district.district_name,
                                    cottage_name=actual_cottage.cottage_name,
                                    congregation_name=actual_congregation.congregation_name)
    db.add(new_elder)
    db.commit()
    db.refresh(new_elder)
    return {"detail": {"message": "Elder created!", "success": True}}


@router.get("/get", status_code=status.HTTP_200_OK, response_model=List[elder_schema.ReadElder])
def get_elders(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    elders = db.query(single_models.Elder).all()
    return elders


@router.get("/get/{ind}", status_code=status.HTTP_200_OK, response_model=elder_schema.ReadElder)
def get_elder(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    elder = db.query(single_models.Elder).filter(single_models.Elder.id == int(ind)).first()

    if not elder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid elder!", "success": False})

    return elder


@router.delete("/delete/{ind}", status_code=status.HTTP_202_ACCEPTED)
def delete_elder(ind: str, db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    elder = db.query(single_models.Elder).filter(single_models.Elder.id == int(ind)).first()
    if not elder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid elder!", "success": False})

    db.delete(elder)
    db.commit()
    return {"detail": {"message": "Elder deleted!", "success": True}}


@router.put("/update/{ind}", status_code=status.HTTP_202_ACCEPTED)
def update_elder(ind: str, request: elder_schema.UpdateElder, db: Session = Depends(get_db),
                 authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    elder_name = request.elder_name
    sex = request.sex
    marital_status = request.marital_status
    telephone = request.telephone
    elder_type = request.elder_type
    date_joined = request.date_joined
    elder_post = request.elder_post

    elder = db.query(single_models.Elder).filter(single_models.Elder.id == int(ind)).first()

    if len(elder_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be greater than five characters!", "success": False})
    if not elder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Elder invalid!", "success": False})
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
    if len(elder_post) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Please enter a valid elder position", "success": False})

    elder.elder_name = elder_name
    elder.sex = sex
    elder.marital_status = marital_status
    elder.telephone = telephone
    elder.date_joined = date_joined
    elder.elder_type = elder_type
    elder.elder_post = elder_post

    db.commit()
    db.refresh(elder)
    return {"detail": {"message": "Elder updated!", "success": True}}


@router.get("/special/get", status_code=status.HTTP_200_OK, response_model=List[elder_schema.ReadElder])
def get_elders(db: Session = Depends(get_db)):

    elders = db.query(single_models.Elder).all()
    return elders


@router.get("/special/get/{ind}", status_code=status.HTTP_200_OK, response_model=elder_schema.ReadElder)
def get_elder(ind: str, db: Session = Depends(get_db)):

    elder = db.query(single_models.Elder).filter(single_models.Elder.id == int(ind)).first()

    if not elder:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid elder!", "success": False})

    return elder
