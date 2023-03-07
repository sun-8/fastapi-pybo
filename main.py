from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

from domain.answer import answer_router
from domain.question import question_router
from domain.user import user_router

# 모든 동작은 이 객체로부터 비롯된다.
app = FastAPI()

# CORS 예외 URL 등록
origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /hello 요청이 발생하면 해당 함수를 실행하여 결과를 리턴한다.
# @app.get("/hello")
# def hello():
#     return {"message": "안녕하세요 파이보~"}

# app 객체에 include_router 메서드를 사용하여 question_router.py 파일의 router 객체를 등록
app.include_router(question_router.router)
# app 객체에 include_router 메서드를 사용하여 answer_router.py 파일의 router 객체를 등록
app.include_router(answer_router.router)
# app 객체에 include_router 메서드를 사용하여 user_router.py 파일의 router 객체를 등록
app.include_router(user_router.router)
# 프론트엔드 빌드를 통해 생성한 파일을 FastAPI 서버가 서비스할 수 있도록 수정
# frontend/dist/assets 디렉터리를 /assets 경로로 매핑할 수 있도록 다음의 설정을 추가
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"))

@app.get("/")
def index():
    # FileResponse는 FastAPI가 정적인 파일을 출력할 때 사용
    return FileResponse("frontend/dist/index.html")

# FastAPI 프로그램 구동 서버
# 1. 터미널 실행 시 powershell이 아닌 cmd창이 나타날 수 있도록 설정
#       파이참 -> Settings -> Terminal -> Shell path -> cmd.exe
# 2. 파이참에서 터미널 실행 후 uvicorn 설치 (pip install "uvicorn[standard]")
# 3. FastAPI 서버 실행 (uvicorn main:app --reload)
#       main => main.py / app => main.py의 app객체 / --reload => 프로그램이 변경되면 서버 재시작 없이 내용반영

# 실행가능한 문서 : /docs
# 읽기만 가능한 문서 : /redoc

# alembic 없이 테이블 생성
# main.py 파일에 다음의 문장을 삽입하면 FastAPI 실행 시 필요한 테이블이 모두 생성
#   import models
#   form datablase import engine
#   models.Base.metadata.create_all(bind=engine)
# 매우 간단하지만 데이터베이스에 테이블이 존재하지 않을 경우에만 테이블을 생성.
# 한번 생성된 테이블에 대한 변경 관리 불가.