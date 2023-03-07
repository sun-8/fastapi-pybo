# 데이터베이스 처리 파일 - crud
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from domain.user.user_schema import UserCreate
from models import User

# bcrypt 알고리즘을 사용하는 pwd_context 객체를 생성하고 pwd_context 객체를 사용하여 비밀번호를 암호화
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, user_create: UserCreate):
    db_user = User(username=user_create.username,
                   password=pwd_context.hash(user_create.password1),
                   email=user_create.email)
    db.add(db_user)
    db.commit()


def get_existing_user(db: Session, user_create: UserCreate):
    return db.query(User).filter(
        (User.username == user_create.username) | (User.email == user_create.email)
    ).first()
    # first() : 첫째를 리밋으로 설정해 scalar(실수 전체집합에 속하는 특정 값)로 가져온다


# 사용자명으로 사용자 모델 객체를 리턴하는 get_user 함수
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()
