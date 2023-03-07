# 라우터 파일 - URL과 API의 전체적인 동작을 관리
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.user import user_schema, user_crud
from domain.user.user_crud import pwd_context

# 토큰의 유효기간을 의미한다. 분 단위로 설정한다.
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
# 암호화시 사용하는 64자리의 랜덤한 문자열이다.
# python 입력 >>> import secrets >>> secrets.token_hex(32)
SECRET_KEY = "d82581ffa180d76c07a84e771aa223bf6ef48ac3b2bd27981f4d80dae50a942e"
# 토큰 생성시 사용하는 알고리즘을 의미하며 여기서는 HS256을 사용한다.
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")

router = APIRouter(
    prefix="/api/user"
)


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(_user_create: user_schema.UserCreate, db: Session = Depends(get_db)):
    user = user_crud.get_existing_user(db, user_create=_user_create)
    if user:
        # 409 : 서버의 현재 상태와 요청이 충돌했음을 나타냄
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="이미 존재하는 사용자입니다.")
    user_crud.create_user(db=db, user_create=_user_create)


# 로그인 API의 입력항목인 username과 password의 값은 OAuth2PasswordRequestForm을 통해 얻어올 수 있음
# 1. username을 사용하여 사용자 모델 객체(user)를 조회하여 가져옴
# 2. 입력으로 받은 password와 데이터베이스에 저장된 사용자의 비밀번호가 일치하는지 조사
#       (이때 회원가입시 사용했던 pwd_context가 사용)
# 3. 만약 데이터베이스에서 해당 사용자를 찾지 못하거나 비밀번호가 일치하지 않는 경우에는 HTTP 401오류를 리턴
#       (401 오류는 사용자 인증 오류를 의미)
#       (보통 401 오류인 경우에는 인증 방식에 대한 추가 정보인 WWW-Authenticate 항목도 헤더 정보에 포함하여 함께 리턴)
@router.post("/login", response_model=user_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):
    # check user and password
    user = user_crud.get_user(db, form_data.username)
    # pwd_context - verify : 암호화 되지 않은 비밀번호를 암호화하여 데이터베이스에 저장된 암호와 일치하는지 판단
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # make access token
    # sub 항목에 사용자명을 저장하고 exp 항목에 토큰의 유효기간을 설정하여 토큰을 생성
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    # jwt(Json Web Token)를 사용하여 액세스 토큰을 생성
    # jwt란 Json 포맷을 이용하여 사용자에 대한 속성을 저장하는 Claim 기반의 Web Token이다.
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


# FastAPI의 Depends는 매개변수로 전달받은 함수를 실행시킨 결과를 리턴
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        # (401 오류는 사용자 인증 오류를 의미)
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # jwt.decode 함수는 토큰을 복호화하여 토큰에 담겨 있는 사용자명을 얻어냄
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        ''' 엥..? 줄이 안맞는데 어케 else: 사용가능..? '''
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        user = user_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user