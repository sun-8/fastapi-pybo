# 라우터 파일 - URL과 API의 전체적인 동작을 관리
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal, get_db
from domain.question import question_schema, question_crud
from domain.user.user_router import get_current_user
from models import Question, User

# 라우터 파일에 반드시 필요한 APIRouter 클래스로 생성한 router 객체를 생성하여 FastAPI 앱에 등록해야 라우팅 기능이 동작
#   라우팅 : FastAPI가 요청받은 URL을 해석하여 그에 맞는 함수를 실행하여 그 결과를 리턴하는 행위
router = APIRouter(
    # 요청 URL에 항상 포함되어야 하는 값 ex)/api/question/*
    prefix="/api/question"
)


# response_model=list[question_schema.Question] : question_list 함수의 리턴값은 Question 스키마로 구성된 리스트임을 의미
@router.get("/list", response_model=question_schema.QuestionList)
def question_list(db: Session = Depends(get_db),
                  page: int = 0, size: int = 10, keyword: str = ''):
    # db 세션을 생성하고 해당 세션을 이용하여 질문 목록을 조회하여 리턴하는 함수
    # 사용한 세션은 db.close()를 수행하여 사용한 세션을 반환
    #   db.close() : 사용한 세션을 커넥션 풀에 반환하는 함수 (세션종료X)
    # db 객체를 생성한 후 db.close()를 수행하지 않으면 SQLAlchemy가 사용하는 커넥션 풀에 db 세션이 반환되지 않아 문제가 생김.
    # db = SessionLocal()
    # _question_list = db.query(Question).order_by(Question.create_date.desc()).all()
    # db.close()

    # with 문을 벗어자는 순간 오류 여부에 상관없이 get_db 함수의 finally에 작성한 db.close() 함수가 자동으로 실행
    # with get_db() as db:
    #     _question_list = db.query(Question).order_by(Question.create_date.desc()).all()

    # get_db 함수를 with 문과 함께 쓰는 대신 question_list 함수의 매개변수로 db: Session = Depends(get_db) 객체를 주입 받음
    # db: Session 문장의 의미는 db 객체가 Session 타입임을 의미 (파이썬 타입 어노테이션 - 변수 : 설정타입 => 변수가 설정타입임을 명시)
    # FastAPI의 Depends는 매개변수로 전달받은 함수를 실행시킨 결과를 리턴
    # db: Session = Depends(get_db)의 db 객체에는 get_db 제너레이터에 의해 생성된 세션 객체가 주입
    # 이 때 get_db 함수에 자동으로 contextmanager가 적용됨.
    # 그래서 database.py의 get_db함수에서 @contextlib.contextmanager 어노테이션을 제거해야함
    # 해당 어노테이션을 제거하지 않으면 2중으로 적용되어 오류발생
    # (Depends에서 contextmanager를 적용하게끔 설계되어있음)
    # _question_list = db.query(Question).order_by(Question.create_date.desc()).all()

    # crud 파일을 사용하여 조회
    # _question_list = question_crud.get_question_list(db)

    total, _question_list = question_crud.get_question_list_paged(
        db, skip=page*size, limit=size, keyword=keyword)
    return {
        'total': total,
        'question_list': _question_list
    }


@router.get("/detail/{question_id}", response_model=question_schema.Question)
def question_detail(question_id: int, db: Session = Depends(get_db)):
    # 매개변수를 db: Session = Depends(get_db), question_id: int 하면 question_id: int에 빨간줄 뜸..
    question = question_crud.get_question(db, question_id=question_id)
    return question


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def question_create(_question_create: question_schema.QuestionCreate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    question_crud.create_question(db=db, question_create=_question_create,
                                  user=current_user)


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def question_update(_question_update: question_schema.QuestionUpdate,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    # QuestionUpdate의 question_id로 db_question을 조회
    db_question = question_crud.get_question(db, question_id=_question_update.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    # db_question의 작성자와 현재 로그인 한 사용자(current_user)가 동일인인지 검증
    if current_user.id != db_question.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="수정 권한이 없습니다.")
    question_crud.update_question(db=db, db_question=db_question,
                                  question_update=_question_update)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def question_delete(_question_delete: question_schema.QuestionDelete,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    db_question = question_crud.get_question(db, question_id=_question_delete.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_question.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    question_crud.delete_question(db=db, db_question=db_question)


@router.post('/vote', status_code=status.HTTP_204_NO_CONTENT)
def question_vote(_question_vote: question_schema.QuestionVote,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    db_question = question_crud.get_question(db, question_id=_question_vote.question_id)
    if not db_question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다")
    question_crud.vote_question(db, db_question=db_question, db_user=current_user)


'''
앞에 하나의 언더바 _variable            : 내부 사용용(internal use only)
뒤에 하나의 언더바 variable_            : 파이썬 키워드와 겹치는 경우를 방지
앞에 둘의 언더바 __variable             : 안에서만 호출이 되는 용도 (접근 지정자의 역할)
앞과 뒤에 두개의 언더바 __variable__     : 매직 메소드(magic method) 혹은 dunder 메소드 (보통 연산자 오버로딩을 할 때 많이 사용)
'''
