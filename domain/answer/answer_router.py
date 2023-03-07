from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from domain.answer import answer_schema, answer_crud
from domain.question import question_crud
from domain.user.user_router import get_current_user
from models import User

router = APIRouter(
    prefix="/api/answer"
)


# 프론트엔드에서 API 호출 시 파라미터로 전달한 content가 AnswerCreate 스키마에 자동으로 매핑
# 출력은 response_model을 사용하는 대신 status_code=status.HTTP_204_NO_CONTENT를 사용
# 리턴할 응답이 없는 경우 응답코드 204를 리턴하여 "응답없음"을 나타냄 (204 : 응답결과없음)
@router.post("/create/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def answer_create(question_id: int,
                  _answer_create: answer_schema.AnswerCreate,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    # create answer
    question = question_crud.get_question(db, question_id=question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    answer_crud.create_answer(db, question=question,
                              answer_create=_answer_create,
                              user=current_user)
    # get_current_user 함수를 사용하여 현재 로그인한 사용자 정보인 current_user 객체를 Depends를 통해 가져옴
    # 이후 답변 데이터 생성시에 파라미터로 전달하여 저장
    # FastAPI의 docs 문서에 접속해 보면 기존에 보이지 않던 "Authorize" 버튼이 생성되어있음
    # 이 버튼이 생긴 이유는 답변 등록 API가 OAuth2PasswordBearer를 통한 인증이 필요한 API로 변경되었기 때문
    # 즉, docs 문서에서 답변등록 API를 사용하려면 "Authorize" 버튼을 통해서 로그인을 먼저 수행해야 함
    # client_id와 client_secret 값은 비워둔채로 진행하면 됨


@router.get("/detail/{answer_id}", response_model=answer_schema.Answer)
def answer_detail(answer_id: int, db: Session = Depends(get_db)):
    answer = answer_crud.get_answer(db, answer_id=answer_id)
    return answer


@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def answer_update(_answer_update: answer_schema.AnswerUpdate,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    db_answer = answer_crud.get_answer(db, answer_id=_answer_update.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_answer.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    answer_crud.update_answer(db=db, db_answer=db_answer, answer_update=_answer_update)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
def answer_delete(_answer_delete: answer_schema.AnswerDelete,
                  db: Session = Depends(get_db),
                  current_user: User = Depends(get_current_user)):
    db_answer = answer_crud.get_answer(db, answer_id=_answer_delete.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    if current_user.id != db_answer.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="삭제 권한이 없습니다.")
    answer_crud.delete_answer(db=db, db_answer=db_answer)


@router.post('/vote', status_code=status.HTTP_204_NO_CONTENT)
def answer_vote(_answer_vote: answer_schema.AnswerVote,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    db_answer = answer_crud.get_answer(db, answer_id=_answer_vote.answer_id)
    if not db_answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    answer_crud.vote_answer(db, db_answer=db_answer, db_user=current_user)