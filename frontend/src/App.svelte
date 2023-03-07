<script>
  import Router from "svelte-spa-router"
  import Home from "./routes/Home.svelte"
  import Detail from "./routes/Detail.svelte"
  import QuestionCreate from "./routes/QuestionCreate.svelte"
  import Navigation from "./components/Navigation.svelte"
  import UserCreate from "./routes/UserCreate.svelte"
  import UserLogin from "./routes/UserLogin.svelte"
  import QuestionModify from "./routes/QuestionModify.svelte"
  import AnswerModify from "./routes/AnswerModify.svelte"

  const routes = {
    '/': Home,                      // /주소에 매핑되는 컴포넌트로 <Home />을 등록. <Home /> : Home.svelte 파일의 내용
    '/detail/:question_id': Detail, // /detail/ 뒤에 붙는 숫자가 가변적이기 때문에 :question_id 라는 URL 규칙을 정의
    '/question-create': QuestionCreate,
    '/user-create': UserCreate,
    '/user-login': UserLogin,
    '/question-modify/:question_id': QuestionModify,
    '/answer-modify/:answer_id': AnswerModify,
  }
</script>

<Navigation/>
<Router {routes}/>

<!-- Svelte 서버 실행하기 : 터미널 - npm run dev -->
<!-- Svelte는 SPA이기 때문에 단 하나의 페이지에서만 내용을 달리해서 표시해야함
      SPA(Single Page Application) : 웹 사이트의 전체 페이지를 하나의 페이지에 담아 동적으로 화면을 바꿔가며 표현하는 것
      대응책으로 Svelte의 svelte-sap-router를 사용 
      서버 중지 후 터미널에 npm install svelte-spa-router 입력-->

<!--
<script>
  let message;

  // FastAPI를 호출하여 돌려받은 값을 message 변수에 담았다.
  // fetch : 서버에 네트워크 요청을 보내고 새로운 정보를 받아옴 (ajax와 비슷. 비동기함수임)
  //    let  promise = fetch(url, [option])
  //    url = 접근하고자 하는 url / option = 선택 매개변수, method나 header를 지정
  fetch("http://127.0.0.1:8000/hello").then((response) => {
    response.json().then((json) => {
      message = json.message;
    })
  })

  // 또다른 fetch 예시
  async function hello() {
    const res = await fetch("http://127.0.0.1:8000/hello");
    const json = await res.json();

    if (res.ok) {
      return json.message;
    } else {
      alert("error");
    }
  }

  let promise = hello();
</script>
-->

<!-- 담겨진 message값을 출력 : undefined => why? CORS 예외
<h1>{message}</h1>
 -->

<!-- 또다른 예시로 한 message값 출력
{#await promise}
  <p>...waiting</p>
{:then message}
  <h1>{message}</h1>
{/await}
 -->

<!-- Svelte 필수 문법

  1. 분기문
  {#if 조건문1}
    <조건문1에 해당하면 html 실행>
  {:else if 조건문2}
    <조건문2에 해당하면 html 실행>
  {/if}

  2. 반복문
  {#each list as item, index}
    <순서 : {index}>
    <{item}>
  {/each}

  3. 객체
  {객체}
  {객체.속성}
-->