<script>
  import fastapi from "../lib/api"
  import {link} from 'svelte-spa-router'
  import { page, keyword, is_login, username } from "../lib/store"
  import moment from 'moment/min/moment-with-locales'
  moment.locale('ko')
  
  // 만약 초기값([])을 주지 않을 경우, fetch 함수는 비동기 방식으로 실행되기 때문에
  // 요청하는 중에 HTML 영역의 each 문이 실행되고 question_list에 값이 없어 오류가 발생
  // 따라서 반복문과 함께 사용할 경우 해당 값을 빈 리스트로 초기화 하거나 해당 값이 있는지 체크하는 로직을 each 문 앞에 사용)
  let question_list = []
  let size = 10
  // let page = 10
  let total = 0
  let kw = ''
  // 전체 페이지 갯수와 게시물의 총 건수는 다르다
  // Math.ceil : 소수값이 존재할 때 값을 올리는 역할 ex)12/10 = 1.2, 전체 페이지 갯수 = 2
  // Svelte에서 $: 기호를 붙이면 해당 변수는 반응형 변수가 됨.
  // 즉, total 변수의 값이 API 호출로 인해 그 값이 변하면 total_page 변수의 값도 실시간으로 재 계산
  $: total_page = Math.ceil(total/size)

  // 페이지 번호를 입력하여 질문 목록 api를 호출 (_page)
  // get_question_list 함수에서 _page 매개 변수를 없애고 $page, $keword와 같은 스토어 변수를 직접 사용
  function get_question_list() {
    let params = {page: $page, size: size, keyword: $keyword}
    fastapi('get', '/api/question/list', params, (json) => {
      question_list = json.question_list
      total = json.total
      kw = $keyword
    })
  }

  // function get_question_list() {
  //   // fetch("http://127.0.0.1:8000/api/question/list").then((response) => {
  //   //   response.json().then((json) => {
  //   //     question_list = json
  //   //   })
  //   // })

  //   // success_callback : (json) => {question_list = json}
  //   // failure_callback 함수를 전달하지 않더라도 fastapi함수는 오류 발생 시 오류의 내용을 alert로 표시하게 되어있음
  //   fastapi('get', '/api/question/list', {}, (json) => {
  //     question_list = json.question_list
  //   })
  // }
  
  // $: 기호는 변수 뿐만 아니라 함수나 구문 앞에 추가하여 사용 가능
  // $: get_question_list($page)의 의미는 page 값이 변경될 경우 get_question_list 함수도 다시 호출
  // $page와 $keyword 스토어 변수를 반응형 변수로 설정
  //    $: 변수1, 변수2, 자바스크립트식 과 같이 사용하면 스벨트는 "변수1" 또는 "변수2"의 값이 변경되는지를 감시하다가 값이 변경되면 자동으로 "자바스크립트식"을 실행
  $: $page, $keyword, get_question_list($page)
</script>
  
<!-- 
  question_list를 State 변수로 지정하지 않아도,
  question_list의 값이 변경되는 순간 그 값이 화면에 실시간으로 반영된다.
  (Svelte가 자랑하는 특징 중 하나인 Truly reactive) 
-->
<!--
  a 태그에 use:link를 사용하는 이유
    a 태그에 use:link 속성을 적용한 링크를 클릭하면 브라우저 주소창에 다음과 같이 표시 => http://127.0.0.1:5173/#/some-path
    즉, /# 문자가 선행되도록 경로가 만들어짐
    브라우저는 이 경로를 하나의 페이지로 인식하여 http://127.0.0.1:5173/#/some-path, http://127.0.0.1:5173/#/question-create
    두 개의 경로를 모두 동일한 페이지로 인식
    해시 기반 라우팅(hash based routing)

  해시 기반 주소를 사용하지 않고 일반 방식의 주소를 사용하는 프론트엔드 파일들을 서버에 적용했다면
  회원 가입을 위한 경로가 요청되어 http://fastapi.pybo.kr/user-create 주소가 표시되는데
  이 상태에서 브라우저를 새로고침하면 브라우저는 fastapi.pybo.kr 서버에 /user-create 라는 경로를 요청하게 된다.
  그러면 서버는 해당 경로를 해석할 수 없어 404 에러가 발생
  /user-create는 서버가 아닌 클라이언트, 즉 프론트엔드에서만 사용하는 경로이기 때문
  해시 기반 주소를 사용하면 http://fastapi.pybo.kr/#/user-create 형태로 주소가 표시되는데
  이런 상태에서 브라우저를 새로고침 하더라도 서버로 요청이 발생하지 않는다.
  브라우저는 /# 으로 시작하는 URL은 동일한 페이지라고 인식하기 때문에 서버로 페이지 요청을 보내지 X
-->

<div class="container my-3">
  <div class="row my-3">
    <div class="col-6">
        <a use:link href="/question-create" 
            class="btn btn-primary {$is_login ? '' : 'disabled'}">질문 등록하기</a>
    </div>
    <div class="col-6">
        <div class="input-group">
          <!-- 검색창의 바인딩 변수를 kw 대신 $keyword를 직접 사용한다면 검색창에 값을 입력할 때마다 질문 목록이 변경될 것 -->
            <input type="text" class="form-control" bind:value="{kw}">
            <button class="btn btn-outline-secondary" on:click={() => {$keyword = kw, $page = 0}}>
                찾기
            </button>
        </div>
    </div>
  </div>
  <table class="table">
    <thead>
    <tr class="text-center table-dark">
      <th>번호</th>
      <th style="width:50%">제목</th>
      <th>글쓴이</th>
      <th>작성일시</th>
    </tr>
    </thead>
    <tbody>
    {#each question_list as question, i}
    <tr class="text-center">
      <td>{total - ($page * size) - i}</td>
      <td class="text-start">
        <a use:link href="/detail/{question.id}">{question.subject}</a>
        {#if question.answers.length > 0}
        <span class="text-danger small mx-2">{question.answers.length}</span>
        {/if}
      </td>
      <td>{question.user ? question.user.username : ""}</td>
      <td>{moment(question.create_date).format("YYYY년 MM월 DD일 hh:mm a")}</td>
    </tr>
    {/each}
    </tbody>
  </table>
  <!-- 페이징처리 시작 -->
  <ul class="pagination justify-content-center">
    <!-- 처음페이지 -->
    <li class="page-item {$page == 0 && 'disabled'}">
      <button class="page-link" on:click={() => {$page = 0}}>처음</button>
    </li>
    <!-- 이전페이지 (-10) -->
    <li class="page-item {$page-9 <= 0 && 'disabled'}">
      <button class="page-link" on:click={() => {$page = $page - 10}}>&lt&lt</button>
    </li>
    <!-- 이전페이지 (-1) -->
    <li class="page-item {$page <= 0 && 'disabled'}">
      <button class="page-link" on:click={() => $page--}>&lt</button>
    </li>
    <!-- 페이지 번호 -->
    {#each Array(total_page) as _, loop_page}
    {#if loop_page >= $page-5 && loop_page <= $page+5}
    <!-- 현재 페이지와 같으면 활성화-->
    <li class="page-item {loop_page === $page && 'active'}">
      <button on:click={() => $page = loop_page} class="page-link">{loop_page+1}</button>
    </li>
    {/if}
    {/each}
    <!-- 다음페이지 (-1) -->
    <li class="page-item {$page >= total_page-1 && 'disabled'}">
      <button class="page-link" on:click={() => $page++}>&gt</button>
    </li>
    <!-- 다음페이지 (-10) -->
    <li class="page-item {$page >= total_page-10 && 'disabled'}">
      <button class="page-link" on:click={() => {$page = $page + 10}}>&gt&gt</button>
    </li>
    <!-- 마지막페이지 -->
    <li class="page-item {$page == total_page-1 && 'disabled'}">
      <button class="page-link" on:click={() => {$page = total_page-1}}>마지막</button>
    </li>
  </ul>
</div>