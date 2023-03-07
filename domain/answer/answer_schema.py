import datetime

from pydantic import BaseModel, validator

from domain.user.user_schema import User


class AnswerCreate(BaseModel):
    content: str

    # content는 필수값이지만 ""같은 공백이 입력되면 X
    # not_empty 함수는 AnswerCreate 스키마에 content 값이 저장될 때 실행.
    # content의 값이 없거나 또는 빈 값인 경우 "빈 값은 허용되지 않습니다." 라는 오류가 발생하도록 함.
    @validator('content')
    def not_empty(cls, v):
        # strip() : 문자열 앞뒤의 공백 또는 특별한 문자 삭제
        if not v or not v.strip():
            # raise : 에러를 발생시킴
            raise ValueError('빈 값은 허용되지 않습니다.')
        return v


class Answer(BaseModel):
    id: int
    content: str
    create_date: datetime.datetime
    user: User | None
    # 프론트엔드에서 답변을 수정한 후에 다시 원래의 질문 상세 화면으로 돌아가기 위해서는 해당 답변이 작성된 질문의 고유번호도 필요
    question_id: int
    # modify_date는 수정이 발생할 경우에만 그 값이 생성되므로 디폴트 값으로 None을 설정
    modify_date: datetime.datetime | None = None
    voter: list[User] = []  # 추천인 정보

    # 조회한 모델의 속성을 스키마에 매핑하기 위해 orm_mode True로 설정
    class Config:
        orm_mode = True

# 입력 항목을 처리하는 스키마가 필요한 이유
#   답변 등록 api는 post 방식이고 content라는 입력 항목이 있는데
#   답변 등록 라우터에서 content의 값을 읽기 위해서는 반드시 content 항목을 포함하는 Pydantic 스키마를 통해 읽어야 한다.
#   스키마를 사용하지 않고 라우터 함수의 매개변수에 content: str을 추가하여 그 값을 읽을 수는 없다.
#   get이 아닌 다른방식의 입력 값은 Pydantic 스키마로만 읽을 수 있기 때문
#   반대로 get 방식의 입력 항목은 Pydantic 스키마로 읽을 수 없고 각각의 입력 항목을 라우터 함수의 매개변수로 읽거야 함
# HTTP 프로토콜의 URL에 포함된 입력값(URL parameter)은 라우터의 스키마가 아닌 매개변수로 읽는다
#   (Path Parameter, Query Parameter)
# HTTP 프로토콜의 Body에 포함된 입력 값(payload)은 Pydantic 스키마로 읽는다
#   (Request Body)


class AnswerUpdate(AnswerCreate):
    answer_id: int


class AnswerDelete(BaseModel):
    answer_id: int


class AnswerVote(BaseModel):
    answer_id: int