<script>
    import moment from 'moment/min/moment-with-locales';
    import { link, push } from 'svelte-spa-router';
    import Error from "../components/Error.svelte";
    import fastapi from "../lib/api";
    import { is_login, username } from "../lib/store";
    import { marked } from 'marked'
    moment.locale('ko')


    // Detail 컴포넌트를 호출할 때 전달한 파라미터 값을 읽으려면 다음과 같이 params 변수를 선언해야함
    export let params = {}
    // 전달된 파라미터 question_id 값은 params.question_id로 읽기 가능
    let question_id = params.question_id
    // console.log('question_id: ' + question_id)

    // 질문 한개에 대한 상세 내용을 리턴하는 질문 상세 API 필요
    // content 항목을 빈 값으로 초기화 하지 않을 경우에 화면 로드시에 marked.parse(quesiton.content)가 데이터 조회전에 실행되어 undefined가 전달되어 오류가 발생
    let question = {answers:[], voter:[], content: ''}
    let content = ""
    let error = {detail:[]}

    function get_question() {
        fastapi('get', '/api/question/detail/' + question_id, {}, (json) => {question = json})
    }

    get_question()

    // 답변 등록
    function post_answer(event) {
        // submit 버튼이 눌릴경우 form이 자동으로 전송되는 것 방지
        event.preventDefault()
        let url = "/api/answer/create/" + question_id
        let params = {
            content: content
        }
        // 답변 등록이 성공하면 등록한 답변이 textarea에서 지워지도록 content에 빈 문자열을 대입
        // 그리고 상세화면에 새로운 결과값을 반영하기 위해 get_question() 함수를 실행
        fastapi('post', url, params, 
            (json) => {
                content = ''
                error = {detail:[]}
                get_question()
            },
            // post_answer 함수 호출 시 오류가 발생하면 해당 함수가 실행되어 오류가 표시
            (err_json) => {
                error = err_json
            }
        )
    }

    // 질문 삭제
    function delete_question(_question_id) {
        if (window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/question/delete"
            let params = {
                question_id: _question_id
            }
            fastapi('delete', url, params, (json) => {push('/')}, (err_json) => {error = err_json})
        }
    }

    // 답변 사게
    function delete_answer(answer_id) {
        if (window.confirm('정말로 삭제하시겠습니까?')) {
            let url = "/api/answer/delete"
            let params = {
                answer_id: answer_id
            }
            fastapi('delete', url, params, (json) => {get_question()}, (err_json) => {error = err_json})
        }
    }

    // 질문 추천
    function vote_question(_question_id) {
        if (window.confirm('정말로 추천하시겠습니까?')) {
            let url = "/api/question/vote"
            let params = {
                question_id: _question_id
            }
            // 질문 추천이 성공하면 get_question 함수가 호출되어 질문 상세 화면이 갱신
            fastapi('post', url, params, (json) => {get_question()}, (err_json) => {error = err_json})
        }
    }

    // 답변 추천
    function vote_answer(_answer_id) {
        if (window.confirm('정말로 추천하시겠습니까?')) {
            let url = "/api/answer/vote"
            let params = {
                answer_id: _answer_id
            }
            // 질문 추천이 성공하면 get_question 함수가 호출되어 질문 상세 화면이 갱신
            fastapi('post', url, params, (json) => {get_question()}, (err_json) => {error = err_json})
        }
    }
</script>

<div class="container my-3">
    <!-- 질문 -->
    <h2 class="border-bottom py-2">{question.subject}</h2>
    <div class="card my-3">
        <div class="card-body">
            <!-- @html은 HTML 코드를 &lt;, &gt; 와 같은 문자열로 변환(strip tags)하지 않고 HTML을 있는 그대로 표시하기 위해 사용 -->
            <div class="card-text">{@html marked.parse(question.content)}</div>
            <div class="d-flex justify-content-end">
                {#if question.modify_date }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">modified at</div>
                    <div>{moment(question.modify_date).format("YYYY년 MM월 DD일 hh:mm a")}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2 text-start">
                    <div class="mb-2">{question.user ? question.user.username : ""}</div>
                    <div>{moment(question.create_date).format("YYYY년 MM월 DD일 hh:mm a")}</div>
                </div>
            </div>
            <div class="my-3">
                <button class="btn btn-sm btn-outline-secondary" on:click="{vote_question(question.id)}"> 
                    추천 <span class="badge rounded-pill bg-success">{ question.voter.length }</span>
                </button>
                <!-- 로그인한 사용자와 글쓴이가 다르면 수정 버튼은 보이지 않음 -->
                {#if question.user && $username === question.user.username}
                <a use:link href="/question-modify/{question.id}"
                    class="btn btn-sm btn-outline-secondary">수정</a>
                <button class="btn btn-sm btn-outline-secondary"
                    on:click={() => delete_question(question.id)}>삭제</button>
                {/if}
            </div>
        </div>
    </div>

    <button class="btn btn-secondary" on:click={() => {push('/')}}>목록으로</button>

    <!-- 답변 목록 -->
    <h5 class="border-bottom my-3 py-2">{question.answers.length}개의 답변이 있습니다.</h5>
    {#each question.answers as answer}
    <div class="card my-3">
        <div class="card-body">
            <!-- style="white-space: pre-line;" => 글 내용의 줄 바꿈을 정상적으로 보여주기 위해 적용한 스타일-->
            <div class="card-text">{@html marked.parse(answer.content)}</div>
            <div class="d-flex justify-content-end">
                {#if answer.modify_date }
                <div class="badge bg-light text-dark p-2 text-start mx-3">
                    <div class="mb-2">modified at</div>
                    <div>{moment(answer.modify_date).format("YYYY년 MM월 DD일 hh:mm a")}</div>
                </div>
                {/if}
                <div class="badge bg-light text-dark p-2 text-start">
                    <div class="mb-2">{answer.user ? answer.user.username : ""}</div>
                    <div>{moment(answer.create_date).format("YYYY년 MM월 DD일 hh:mm a")}</div>
                </div>
            </div>
            <div class="my-3">
                <button class="btn btn-sm btn-outline-secondary" on:click="{vote_answer(answer.id)}"> 
                    추천 <span class="badge rounded-pill bg-success">{ answer.voter.length }</span>
                </button>
                {#if answer.user && $username === answer.user.username }
                <a use:link href="/answer-modify/{answer.id}" 
                    class="btn btn-sm btn-outline-secondary">수정</a>
                <button class="btn btn-sm btn-outline-secondary"
                    on:click={() => delete_answer(answer.id) }>삭제</button>
                {/if}
            </div>
        </div>
    </div>
    {/each}
    <!-- 답변 등록-->
    <Error error={error}/>
    <form method="post" class="my-3">
        <div class="mb-3">
            <!-- 텍스트 창에 작성한 내용은 스크립트 영역에 추가한 content 변수와 연결되도록 bind:value={content} 속성을 사용 -->
            <!-- textarea에 값을 추가하거나 변경할 때마다 content의 값도 자동으로 변경-->
            <textarea rows="10" bind:value={content} 
                class="form-control"
                disabled={$is_login ? "" : "disabled"}/>
        </div>
        <input type="submit" value="답변등록" class="btn btn-primary {$is_login ? '' : 'disabled'}" on:click="{post_answer}"/>
    </form>
</div>