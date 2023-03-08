import contextlib

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.config import Config

config = Config('.env')
SQLALCHEMY_DATABASE_URL = config('SQLALCHEMY_DATABASE_URL')

# database 접속주소 => sqlite3 데이터베이스의 파일을 의미하며 프로젝트 루트 디렉터리에 저장한다는 의미
SQLALCHEMY_DATABASE_URL = "sqlite:///./myapi.db"

# create_engine : 커넥션 출을 생성
#   커넥션 풀 : database에 접속하는 객체를 일정 갯수만큼 만들어 놓고 돌려가며 사용하는 것.
#   (database에 접속하는 세션 수를 제어하고, 세션 접속에 소요되는 시간을 줄이고자 하는 용도)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
# database에 접속하기 위해 필요한 클래스
# autocommit = False : 데이터를 변경했을 때 commit이라는 사인을 주어야만 실제 저장됨. rollback 가능.
# (autocommit = True : 즉시 적용, rollback 불가)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스는 database 모델을 구성할 때 사용되는 클래스
Base = declarative_base()
# SQLite 데이터베이스에만 해당하는 오류
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
# MetaData 클래스를 사용하여 데이터베이스의 프라이머리 키, 유니크 키, 인덱스 키 등의 이름 규칙을 새롭게 정의
# 데이터베이스에서 디폴트 값으로 명명되던 프라이머리 키, 유니크 키 등의 제약조건 이름을 수동으로 설정
Base.metadata = MetaData(naming_convention=naming_convention)

# FastAPI의 Dependency Injection(의존성 주입)을 사용하여 데이터베이스 세션의 생성화 반환을 자동화
#   Dependency Injection(의존성 주입) : 필요한 기능을 선언하여 사용할 수 있다는 의미
# @contextlib.contextmanager
def get_db():
    # db 세션 객체를 리턴하는 제너레이터인 get_db 함수
    #   제너레이터 : 함수가 연속된 값을 차례대로 반환. 차례대로 결과를 반환하고자 return 대신 yield 키워드를 사용. (하나의 객체임)
    #   ex) return "abc" => abc / yield "a" = a, yield "b" = b, yield "c" = c
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

''' 데이터 삽입
(myapi) C:\project\myapi>python => 파이썬 셸 실행 (파이썬 셸 종료 : ctrl+z 후 <Enter> 입력 / quit() 입력)
>>> from models import Question, Answer
>>> from datetime import datetime
>>> q = Question(subject='pybo가 무었인가요?', content='pybo에 대해서 알고싶습니다.', create_date=datetime.now())
>>> from database import SessionLocal
>>> db = SessionLocal()
>>> db.add(q)
>>> db.commit()
>>> q.id
1
'''

''' 데이터 조회
# 모든 데이터 조회
>>> db.query(Question).all()
[<models.Question object at 0x0000019C9E547850>, <models.Question object at 0x0000019C9B182450>]
# 조건에 맞는 데이터 조회
>>> db.query(Question).filter(Question.id==1).all()
[<models.Question object at 0x0000019C9E547850>]
# get함수를 이용한 리턴은 1건이라서 리스트가 아닌 Question 객체가 리턴
>>> db.query(Question).get(1)
<models.Question object at 0x0000019C9E547850>
# filter와 like로 제목에 "FastAPI"라는 문자열이 포함된 질문을 조회
>>> db.query(Question).filter(Question.subject.like('%FastAPI%')).all()
[<models.Question object at 0x0000019C9B182450>]

# FastAPI% : "FastAPI"로 시작하는 문자열
# %FastAPI : "FastAPI"로 끝나는 문자열
# %FastAPI% : "FastAPI"를 포함하는 문자열
'''

''' 데이터 수정
>>> q = db.query(Question).get(2)
>>> q.id
2
>>> q.subject = 'FastAPI Model Question'
>>> db.commit()
>>> q.subject
'FastAPI Model Question'
'''

''' 데이터 삭제 (삭제 했을 때 전체 조회 시 하나만 결과가 나오지만 q를 조회했을 때 값이 나온다?)
>>> q = db.query(Question).get(1)
>>> db.delete(q)
>>> db.commit()
>>> db.query(Question).all()
[<models.Question object at 0x0000019C9E56A7D0>]
>>> q.id
1
>>> q.subject
'pybo가 무었인가요?'
'''

''' 외부키가 있는 데이터 삽입
>>> from datetime import datetime
>>> from models import Question, Answer
>>> from database import SessionLocal
>>> db = SessionLocal()
>>> q = db.query(Question).get(2)
>>> a = Answer(question=q, content='네 자동으로 생성됩니다.', create_date=datetime.now())
>>> db.add(a)
>>> db.commit()

# Answer 모델에는 어떤 질문에 해당하는 답변인지 연결할 목적인 question_id 속성이 있지만
# Answer 모델의 객체를 생성할 때 question에 q를 대입하면 question_id에 값을 지정하지 않아도 자동으로 입력되어 저장
# 즉, question_id에 값을 설정할 필요 X
'''

''' 답변에 연결된 질문 찾기 VS 질문에 달린 답변 찾기
>>> a = db.query(Answer).get(1)
>>> a
<models.Answer object at 0x0000019C9E55DC50>
>>> a.question
<models.Question object at 0x0000019C9E576E10>

>>> q = db.query(Question).get(2)
>>> q 
<models.Question object at 0x0000019C9E576E10>
>>> q.answers
[<models.Answer object at 0x0000019C9E55DC50>]
'''