from sqlalchemy import Integer, Column, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship

from database import Base


# question_voter 는 질문 추천을 위해 사용할 테이블 객체
# ManyToMany 관계를 적용하기 위해서는 sqlalchemy의 Table을 사용하여 N:N 관계를 의미하는 테이블을 먼저 생성
# question_voter 테이블 객체 생성시 사용한 첫번째 인수인 'question_voter'는 테이블명을 의미
# question_voter는 사용자 id와 질문 id를 쌍으로 갖는 테이블 객체
# 사용자 id와 질문 id가 모두 PK(프라이머리키)이므로 ManyToMany 관계가 성립
#   (한 명의 사용자가 여러개의 질문을 추천할 수 있고 반대로 한 개의 질문을 여러명이 추천할 수 있는 구조)
# user_id와 question_id 는 프라이머리키이므로 두개의 값이 모두 같은 데이터는 저장될 수 없다.
question_voter = Table(
    'question_voter',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('question_id', Integer, ForeignKey('question.id'), primary_key=True)
)


# Question Class (질문 모델)
# Question 모델 클래스는 Base 클래스를 상속하여 만든다.
class Question(Base):
    # 모델에 의해 관리되는 테이블의 이름을 뜻함
    __tablename__ = "question"

    # 각 속성은 Column으로 생성
    # Column()안의 첫번째 인수는 데이터 타입을 의미
    # Column()안의 두번째 인수는 속성을 추가로 설정
    #   primary key : 데이터 타입이 Integer이고 기본키로 설정한 속성은 값이 자동으로 증가하는 특징이 있어
    #                   데이터를 저장할 때 값을 세팅하지 않아도 1씩 자동으로 증가되어 저장된다.
    #   nullable : null을 허용하지 않으려면 False (기본값 null 허용)
    id = Column(Integer, primary_key=True)  # 고유번호
    subject = Column(String, nullable=False)  # 제목
    content = Column(Text, nullable=False)  # 내용 (Text : 글자 수를 제한할 수 없는 텍스트)
    create_date = Column(DateTime, nullable=False)  # 작성일시
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True) # User 모델을 Question 모델과 연결하기 위한 속성
    user = relationship("User", backref="question_users")  # user 속성은 Question 모델에서 User 모델을 참조하기 위한 속성
    modify_date = Column(DateTime, nullable=True)  # 수정 일시

    # voter는 추천인이므로 기본적으로 User 모델과 연결된 속성
    # secondary 값으로 위에서 생성한 question_voter 테이블 객체를 지정
    # 이렇게 하면 Question 모델을 통해 추천인을 저장했을 때 실제 데이터는 question_voter 테이블에 저장
    # 저장된 추천인 정보는 Question 모델의 voter 속성을 통해 참조
    # voter의 backref 이름은 question_voters 라는 이름으로 지정
    #  ex) 어떤 계정이 a_user 라는 객체로 참조되었다면 a_user.question_voters 으로 해당 계정이 추천한 질문 리스트를 조회
    # !!!!! backref 이름은 중복될수 없다. !!!!!
    voter = relationship('User', secondary=question_voter, backref='question_voters')


answer_voter = Table(
    'answer_voter',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('answer_id', Integer, ForeignKey('answer.id'), primary_key=True)
)


# Answer Class (답변 모델)
class Answer(Base):
    __tablename__ = "answer"

    id = Column(Integer, primary_key=True)  # 답변 고유번호
    content = Column(Text, nullable=False)  # 답변 내용
    create_date = Column(DateTime, nullable=False)  # 답변 작성일시

    # 외부 키 사용 (question.id는 question 테이블의 id 컬럼을 의미. question 객체의 속성 id X)
    #   Question 모델을 통해 테이블이 생서되면 테이블명은 question이 됨. (__tablename__ = "~")
    question_id = Column(Integer, ForeignKey("question.id"))  # 질문 고유번호

    # 답변 모델에서 질문 모델을 참조하기 위해 추가
    # relationship으로 question 속성을 생성하면 답변 객체에서 연결된 질문의 제목을 answer.question.subject 처럼 참조 가능
    # relationship의 첫번째 인자값은 참조할 모델명, 두번째 backref 인자는 역참조 설정
    #   역참조 : 질문에서 답변을 거꾸로 참조하는 것.
    #   ex) 어떤 질문에 해당하는 객체가 a_question, a_question.answers와 같은 코드로 해당 질문에 달린 답변들을 참조
    question = relationship("Question", backref="answers")  #
    user_id = Column(Integer, ForeignKey("user.id"), nullable=True) # User 모델을 Answer 모델과 연결하기 위한 속성
    user = relationship("User", backref="answer_users")  # user 속성은 Answer 모델에서 User 모델을 참조하기 위한 속성
    modify_date = Column(DateTime, nullable=True)  # 수정 일시
    voter = relationship('User', secondary=answer_voter, backref='answer_voters')


# User Class (회원 모델)
class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# SQLAlchemy의 alembic을 이용해 데이터베이스 테이블을 생성
# alembic : SQLAlchemy로 작성한 모델을 기반으로 데이터베이스를 쉽게 관리할 수 있게 도와주는 도구 (모델을 테이블 생성, 변경 가능)
# > pip install alembic
# alembic 설치 후 초기화 작업을 진행
# > alembic init migrations
# myapi 디렉터리 하위에 migrations라는 디렉터리와 alembic.ini 파일이 생성됨
#   migrations 디렉터리 : alembic 도구를 사용할 때 생성되는 리비전 파일들을 저장하는 용도
#       리비전 - 테이블을 생성 또는 변경할 때마다 생성되는 작업파일
#   alembic.ini 파일 : alembic의 환경설정 파일
