# 데이터베이스 처리 파일 - crud
# 현재 라우터에 _question_list = db.query(Question).order_by(Question.create_date.desc()).all()로 조회하는 부분을 포함
# 데이터를 처리하는 부분을 파일을 따로 분리하여 작성.
# 서로 다른 라우터에서 데이터를 처리하는 부분이 동일하여 중복될 수도 있기 때문 (이 파일을 만드는 것은 필수가 아님)
from datetime import datetime

from sqlalchemy.orm import Session

from domain.question.question_schema import QuestionCreate, QuestionUpdate
from models import Question, User, Answer


# question 리스트
def get_question_list(db: Session):
    question_list = db.query(Question) \
        .order_by(Question.create_date.desc()) \
        .all()
    return question_list


# question 리스트 (페이징)
def get_question_list_paged(db: Session, skip: int = 0, limit: int = 10, keyword: str = ''):
    '''엥..? skip: int = 0, limit: int = 10, db: Session 이렇게 하면 빨간줄 뜸'''
    # skip : 조회한 데이터의 시작위치
    # limit : 시작위치부터 가져올 데이터의 건수
    question_list = db.query(Question)
    if keyword:
        search = '%%{}%%'.format(keyword)
        sub_query = db.query(Answer.question_id, Answer.content, User.username) \
            .outerjoin(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .outerjoin(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |     # 질문제목
                    Question.content.ilike(search) |     # 질문내용
                    User.username.ilike(search) |        # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)   # 답변작성자
                    )
    total = question_list.distinct().count()
    question_list = question_list.order_by(Question.create_date.desc()) \
        .offset(skip).limit(limit).distinct().all()
    # 전체 건수 total은  offset, limit을 적용하기 전에 먼저 구해야함
    # 페이징이 이미 적용된 질문 목록에 count()함수를 사용한다면 limit 값에 해당되는 10이 리턴
    # 전체 건수, 페이징 적용된 질문 목록
    return total, question_list


# question 상세
def get_question(db: Session, question_id: int):
    question = db.query(Question).get(question_id)
    return question


# question 등록
def create_question(db: Session, question_create: QuestionCreate, user: User):
    db_question = Question(subject=question_create.subject,
                           content=question_create.content,
                           create_date=datetime.now(),
                           user=user)
    db.add(db_question)
    db.commit()


# question 수정
# Question 모델과 QuestionUpdate 스키마를 입력받아 질문 데이터를 수정하는 update_question 함수를 작성
def update_question(db: Session, db_question: Question,
                    question_update: QuestionUpdate):
    db_question.subject = question_update.subject
    db_question.content = question_update.content
    db_question.modify_date = datetime.now()
    db.add(db_question)
    db.commit()


# question 삭제
def delete_question(db: Session, db_question: Question):
    db.delete(db_question)
    db.commit()


# question 추천
# Question 모델의 voter에 추천인을 추가하는 vote_question 함수
#   (Question 모델의 voter는 question_voter 테이블과 연결된 속성)
def vote_question(db: Session, db_question: Question, db_user: User):
    db_question.voter.append(db_user)
    db.commit()