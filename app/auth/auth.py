from typing import Annotated
from fastapi import Depends, APIRouter, status, HTTPException
# from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from ..schemas.user import UserCreateSchema, UserReadSchema, UserLoginSchema
from ..dependencies import get_session
from . import utilits
from ..models.models import User

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

router = APIRouter(prefix="/auth", tags=["auth"])

# reginster user
@router.post("/register", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED)
def register_user(register_data: UserCreateSchema, session: Annotated[Session, Depends(get_session)]):
    """
    User registration endpoint
    
    **register_data**: form data containing user registration details
    **session**: database session dependency
    """
    # Copy register_data to modify
    user_form = register_data.model_copy()

    # password hashing
    hash_password = utilits.hash_password(register_data.password)
    user_form.password = hash_password

    # Mapping UserCreateSchema to User model
    user = User(**user_form.model_dump(exclude_unset=True), hashed_password=hash_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# login user
@router.post("/login", status_code=status.HTTP_202_ACCEPTED, response_model=UserReadSchema)
def login_user(login_data: UserLoginSchema, session: Annotated[Session, Depends(get_session)]):
    """
    User login endpoint
    
    **login_data**: form data containing user login details
    **session**: database session dependency
    """
    creditals_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail={"error": "Invalid email or password"}
        )
    statement = select(User).where(User.email == login_data.email)
    user = session.exec(statement).first()
    if not user:
        raise creditals_error

    # verify password
    is_valid_password = utilits.verify_password(login_data.password, user.hashed_password)
    if not is_valid_password:
        raise creditals_error

    return user
    