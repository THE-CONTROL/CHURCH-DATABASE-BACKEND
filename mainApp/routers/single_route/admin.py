from fastapi import APIRouter, Depends, status, HTTPException
from mainApp.schemas.single import admin_schema
from mainApp.schemas.group import congregation_schema
from mainApp.data.all_database import single_models, group_models
from sqlalchemy.orm import Session
from mainApp.data.database import get_db
import bcrypt
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from fastapi_jwt_auth.exceptions import AuthJWTException
import validators
import secrets
import string
from mainApp.utils.email import send_mail
from datetime import datetime


router = APIRouter(prefix="/admin", tags=["admin"])


class Settings(BaseModel):
    authjwt_secret_key: str = '7a1fd21e19813b07264649b20a621a548b32bf1c6053d5bac1f114794c63470c'


@AuthJWT.load_config
def get_config():
    return Settings()


@router.post("/register", status_code=status.HTTP_201_CREATED,)
async def create_admin(request: admin_schema.RegisterAdmin, db: Session = Depends(get_db)):
    admin_name = request.admin_name
    password = request.password
    role = request.role
    email = request.email
    confirm_password = request.confirm_password

    taken_admin_name = db.query(single_models.Admin).filter(single_models.Admin.admin_name == admin_name).first()
    admin_email = db.query(single_models.Admin).filter(single_models.Admin.email == email).first()

    if len(admin_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be at least five characters!", "success": False})
    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Password must be greater than five characters!",
                                    "success": False})
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Passwords don't match!", "success": False})
    if len(role) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Role must be greater than five characters!",
                                    "success": False})
    if taken_admin_name:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"message": "Admin with same name already registered!", "success": False})
    if admin_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"message": "Admin with same email already registered!", "success": False})
    if not validators.email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Enter a valid email address!", "success": False})

    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    subject = "Hello from Church Database"
    message = f"Welcome {admin_name}. Your account has been created and is active!"
    email_list = [email]

    try:
        await send_mail(subject=subject, recipient=email_list, message=message)
    except Exception as e:
        return {"detail": {"message": e, "success": False}}

    new_admin = single_models.Admin(admin_name=admin_name, password=password, role=role, email=email)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return {"detail": {"message": "Admin created!", "success": True}}


@router.post("/login", status_code=status.HTTP_200_OK)
def login_admin(request: admin_schema.LoginAdmin, authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    admin_name = request.admin_name
    password = request.password

    admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == admin_name).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid admin details!", "success": False})
    if not bcrypt.checkpw(password.encode('utf-8'), admin.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid admin details!", "success": False})
    access_token = authorize.create_access_token(subject=admin.admin_name)
    refresh_token = authorize.create_refresh_token(subject=admin.admin_name)

    admin.logged_in = True
    db.commit()
    db.refresh(admin)

    return {"detail": {"message": "Login successful", "success": True, "access_token": access_token,
            "refresh_token": refresh_token}}


@router.get("/logged_in/get", status_code=status.HTTP_200_OK, response_model=admin_schema.Admin)
def get_admin(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()

    admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == current_admin).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid admin!", "success": False})

    return admin


@router.get("/congregation/get", status_code=status.HTTP_200_OK,
            response_model=congregation_schema.AllCongregation)
def get_admin_congregation(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()

    try:
        congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == current_admin).first()

        if not congregation:
            raise Exception
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={"congregation": congregation})

    return congregation


@router.delete("/delete", status_code=status.HTTP_202_ACCEPTED)
async def delete_admin(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()

    admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == current_admin).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid admin!", "success": False})

    subject = "Goodbye from Church Database"
    message = f"Welcome {current_admin}. Your account has been deleted and is no longer active!"
    email_list = [admin.email]

    try:
        await send_mail(subject=subject, recipient=email_list, message=message)
    except Exception as e:
        return {"detail": {"message": e, "success": False}}

    db.delete(admin)
    db.commit()
    return {"detail": {"message": "Admin deleted!", "success": True}}


@router.put("/update", status_code=status.HTTP_202_ACCEPTED)
async def update_admin(request: admin_schema.UpdateAdmin, db: Session = Depends(get_db),
                       authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()

    admin_name = request.admin_name
    role = request.role
    email = request.email

    taken_admin_name = db.query(single_models.Admin).filter(single_models.Admin.admin_name == admin_name).first()
    admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == current_admin).first()
    admin_email = db.query(single_models.Admin).filter(single_models.Admin.email == email).first()
    congregation = db.query(group_models.Congregation).\
        filter(group_models.Congregation.admin_name == admin.admin_name).first()

    if len(admin_name) < 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Name must be at least five characters!", "success": False})
    if not admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid admin!", "success": False})
    if len(role) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Role must be greater than five characters!",
                                    "success": False})
    if taken_admin_name and taken_admin_name != admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"message": "Admin with same name already registered!", "success": False})
    if admin_email and admin_email != admin:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail={"message": "Admin with same email already registered!", "success": False})
    if not validators.email(email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Enter a valid email address!", "success": False})

    subject = "Account Updates from Church Database"
    message = f"Hi {admin_name}. Your account has been edited!"
    email_list = [email]

    try:
        await send_mail(subject=subject, recipient=email_list, message=message)
    except Exception as e:
        return {"detail": {"message": e, "success": False}}

    if congregation:
        congregation.admin_name = admin_name

    admin.admin_name = admin_name
    admin.role = role
    admin.email = email

    db.commit()
    db.refresh(admin)
    return {"detail": {"message": "Admin updated, Log in to restart!", "success": True}}


@router.put("/logout", status_code=status.HTTP_202_ACCEPTED)
def logout_admin(db: Session = Depends(get_db), authorize: AuthJWT = Depends()):
    try:
        authorize.jwt_required()
    except AuthJWTException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail={"message": "User Unauthorised!", "success": False})

    current_admin = authorize.get_jwt_subject()

    admin = db.query(single_models.Admin).filter(single_models.Admin.admin_name == current_admin).first()

    admin.logged_in = False

    db.commit()
    db.refresh(admin)
    return {"detail": {"message": "Logout successful!", "success": True, "admin": admin}}


@router.post('/refresh')
def refresh(authorize: AuthJWT = Depends()):
    authorize.jwt_refresh_token_required()

    current_admin = authorize.get_jwt_subject()
    access_token = authorize.create_access_token(subject=current_admin)
    return {"access_token": access_token}


@router.post("/forgot_password")
async def forgot_password(request: admin_schema.ForgotPassword, db: Session = Depends(get_db)):
    email = request.email
    email_list = [email]

    admin = db.query(single_models.Admin).filter(single_models.Admin.email == email).first()

    if not admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Admin with email does not exist!", "success": False})

    alphabet = string.ascii_letters + string.digits
    reset_code = ''.join(secrets.choice(alphabet) for i in range(10))

    new_code = single_models.ResetPassword(email=email, reset_code=reset_code, status="1")
    db.add(new_code)
    db.commit()
    db.refresh(new_code)

    subject = "Reset Your Password"
    message = f"Your admin name is {admin.admin_name}. Your reset code is {reset_code}. It expires in 5 minutes"

    try:
        await send_mail(subject=subject, recipient=email_list, message=message)

        return {"detail": {"message": "We've sent a reset code to your email address!", "success": True}}
    except Exception as e:
        return {"detail": {"message": e, "success": False}}


@router.post("/reset_code")
def check_reset_code(request: admin_schema.Reset, db: Session = Depends(get_db)):
    code = request.code
    password = request.password
    confirm_password = request.confirm_password

    reset = db.query(single_models.ResetPassword).filter(single_models.ResetPassword.reset_code == code).first()
    if not reset:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid reset code!", "success": False})
    if len(password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Password must be greater than five characters!",
                                    "success": False})
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Passwords don't match!", "success": False})

    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    admin = db.query(single_models.Admin).filter(single_models.Admin.email == reset.email).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Invalid admin!", "success": False})

    if datetime.utcnow() > reset.expires_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail={"message": "Reset code expired", "success": False})

    admin.password = password

    db.commit()
    db.refresh(admin)
    return {"detail": {"message": "Admin password updated!", "success": True}}
