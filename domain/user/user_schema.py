# 입출력 관리 파일 - 입력 데이터와 출력 데이터의 스펙 정의 및 검증
from pydantic import BaseModel, EmailStr, validator


class UserCreate(BaseModel):
    username: str
    password1: str
    password2: str
    email: EmailStr

    @validator('username', 'password1', 'password2', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v

    @validator('password2')
    def passwords_match(cls, v, values):
        if 'password1' in values and v != values['password1']:
            raise ValueError('비밀번호가 일치하지 않습니다')
        return v


# FastAPI의 OAuth2 인증을 사용 - fastapi의 security 패키지를 이용
# OAuth2는 인증 및 권한 부여를 처리하기 위해 사용하는 인증방식 (페이스북, 구글, 트위터, 깃허브와 같은 시스템도 OAuth2 인증 방식을 따름)
# 로그인 후 받아온 액세스 토큰은 질문 작성, 답변 작성등 로그인이 필요한 API를 호출할때 필요
# FastAPI의 라우팅 함수는 HTTP 헤더에 담긴 액세스 토큰을 통해 사용자명과 토큰의 유효기간을 얻을 수 있음
# 따라서 프론트엔드는 로그인의 결과로 받은 액세스 토큰을 저장해 두었다가 API를 호출 할 때마다 HTTP 헤더에 액세스 토큰을 담아 요청해아 함
# 로그인 API의 입력 스키마는 fastapi의 security 패키지에 있는 OAuth2PasswordRequestForm 클래스를 사용하므로 따로 만들 필요가 없음
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


class User(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True