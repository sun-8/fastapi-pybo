# 입출력 관리 파일 - 입력 데이터와 출력 데이터의 스펙 정의 및 검증
import datetime

from pydantic import BaseModel, validator

from domain.answer.answer_schema import Answer
from domain.user.user_schema import User


# Pydantic
# 외부로 공개되면 안되는 출력항목이 있거나 출력 값이 정확한지 검증할 때 사용
# FastAPI의 입출력 스펙을 정의하고 그 값을 검증하기 위해 사용하는 라이브러리
# FastAPI 설치시 함께 설치되기 때문에 따로 설치 필요X
# API의 입출력 항목을 아래와 같이 정의하고 검증 가능
#   입출력 항목의 갯수와 타입을 설정
#   입출력 항목의 필수값 체크
#   입출력 항목의 데이터 검증


# BaseModel을 상속한 Question 클래스 생성 => Question 스키마
#   스키마 : 데이터의 구조와 명세. ex)출력스키마 - 출력 항목, 제약 조건
class Question(BaseModel):
    # 정해진 타입이 아닌 다른 타입의 자료형이 대입되면 오류발생
    # 디폴트 값이 없기 때문에 필수항목임을 나타냄
    # 만약 subject 항목이 필수항목이 아니게 되면 subject: str | None = None (문자열 또는 None을 가질 수 있고 디폴트 값은 None)
    # 만약 Question 스키마에서 content 항목을 제거한다면 질문 목록 API의 출력 항목에도 content 항목이 제거됨
    #   이 때, 실제 리턴되는 _question_list를 수정할 필요 없이 스키마에서만 제외하면 되니 편리
    id: int
    subject: str
    content: str
    create_date: datetime.datetime
    answers: list[Answer] = []
    user: User | None
    # modify_date는 수정이 발생할 경우에만 그 값이 생성되므로 디폴트 값으로 None을 설정
    modify_date: datetime.datetime | None = None
    voter: list[User] = []  # 추천인 정보

    # Question 스키마에 Answer 스키마로 구성된 answers 리스트를 추가
    # Answer 모델은 Question 모델과 answers라는 이름으로 연결되어있음.
    # Answer 모델에 Question 모델을 연결할 때 backref="answers" 속성을 지정했기 때문
    # Question 스키마에도 answers라는 이름의 속성을 사용해야 등록된 답변들이 정확하게 매핑
    # 만약 answers 대신 다른 이름을 사용한다면 값이 채워지지 않음

    # pydantic.error_wrappers.ValidationError: 1 validation error for Question
    # response -> 0
    # value is not a valid dict(type=type_error.dict)
    # 리턴값에 해당되는 _question_list의 요소값이 딕셔너리가 아닌 Question 모델
    # Question 모델은 Question 스키마로 자동 변환되지 않는다.
    # 아래의 설정으로 Question 모델의 항목들이 Question 스키마로 매핑
    class Config:
        orm_mode = True


class QuestionCreate(BaseModel):
    subject: str
    content: str

    @validator('subject', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('빈 값은 허용되지 않습니다')
        return v


class QuestionList(BaseModel):
    total: int = 0
    # list[Question]에서 Question은 반드시 앞에 있어야함
    question_list: list[Question] = []


class QuestionUpdate(QuestionCreate):
    # QuestionCreate 스키마에 이미 subject, content 항목이 있으므로 QuestionCreate 스키마를 상속하고 question_id 항목만 추가
    # QuestionCreate를 상속했으므로 QuestionCreate에 있는 not_empty와 같은 검증 메서드도 동일하게 동작
    question_id: int


class QuestionDelete(BaseModel):
    question_id: int


class QuestionVote(BaseModel):
    question_id: int