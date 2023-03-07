import qs from "qs"
import { push } from "svelte-spa-router";
import { access_token, username, is_login } from "./store";
import { get } from 'svelte/store'

const fastapi = (operation, url, params, success_callback, failure_callback) => {
  // operation : 데이터를 처리하는 방법 (get, post, put, delete)
  // url : 요청 URL, 단 백엔드 서버의 호스트명 이후의 URL만 전달 (/api/question/list)
  // params : 요청데이터 ({page: 1, keyword: "마크다운" })
  // success_callback : API 호출 성공 시 수행할 함수, 전달된 함수에는 API 호출시 리턴되는 json이 입력으로 주어짐
  // failure_callback : API 호출 실패 시 수행할 함수, 전달된 함수에는 오류 값이 입력으로 주어짐
  let method = operation;
  let content_type = "application/json";
  let body = JSON.stringify(params);

  if (operation === 'login') {
    method = 'post'
    // OAuth2를 사용하여 로그인 할때 Content-Type을 application/x-www-form-urlencoded로 사용해야 하는 것은 OAuth2의 규칙
    content_type = 'application/x-www-form-urlencoded'
    // params 데이터를 'application/x-www-form-urlencoded' 형식에 맞게끔 변환하는 역할
    body = qs.stringify(params)
  }

  // .env 파일에 등록한 VITE_SERVER_URL 변수 호출방식 : import.meta.env.VITE_SERVER_URL
  let _url = import.meta.env.VITE_SERVER_URL + url;
  if (method === "get") {
    _url += "?" + new URLSearchParams(params);
  }

  let options = {
    method: method,
    headers: {
      "Content-Type": content_type,
    },
  };

  // fastapi 함수를 이용하여 API 호출시 HTTP 헤더에 액세스 토큰을 담아서 호출
  // 이러한 과정이 없다면 질문 등록 또는 답변 등록시 항상 401 Unauthorized 오류
  // svelte 컴포넌트가 아닌 fastapi 함수는 스토어 변수를 사용할 때 $access_token 처럼 $ 기호로 참조할 수 없음
  // 따라서 스토어 변수의 값을 읽으려면 get 함수를 사용해야 하고 값을 저장할때는 access_token.set 처럼 set 함수를 사용
  const _access_token = get(access_token)
  if (_access_token) {
    // 스토어 변수인 access_token에 값이 있을 경우에 HTTP 헤더에 Authorization 항목을 추가
    // Authorization 헤더 항목의 값은 "Bearer" 문자열에 띄어쓰기 한 칸을 한 후에 액세스 토큰을 더하여 만들어야 함
    options.headers["Authorization"] = "Bearer " + _access_token
  }

  if (method !== "get") {
    // get이 아닌 경우 options['body']에 전달받은 파라미터 값을 설정하게 함.
    // body 항목에 값을 설정할 때는 JSON.stringify(params)처럼 params를 JSON 문자열로 변경해야함.
    options['body'] = body;
  }

  fetch(_url, options).then((response) => {
    // 응답결과(json)가 있을 때만 success_callback을 실행하도록 했지만
    // 응답상태코드가 204인 경우 응답결과가 없더라도 success_callback을 실행할 수 있도록 수정
    if (response.status === 204) { // No content
      if (success_callback) {
        // 응답결과가 없기 때문에 파라미터 없이 함수만 호출
        success_callback()
      }
      // success_callback을 호출 후 뒤의 코드가 실행되지 않도록 return 처리
      return
    }
    response.json().then((json) => {
      if (response.status >= 200 && response.status < 300) { // 200 ~ 299
        if (success_callback) {
          success_callback(json);
        }
      } else if (operation !== 'login' && response.status === 401) { // token time out
        // operation이 'login' 인 경우는 아이디 또는 비밀번호를 틀리게 입력했을 경우에 401 오류가 발생하므로 제외
        // (유효기간이 종료된 토큰을 사용할 경우에도 401 오류가 발생)
        access_token.set('')
        username.set('')
        is_login.set(false)
        alert("로그인이 필요합니다.")
        push('/user-login')
      } else {
        if (failure_callback) {
          failure_callback(json);
        } else {
          alert(JSON.stringify(json));
        }
      }
    })
    .catch(error => {
      alert(JSON.stringify(error));
    });
  });
};

export default fastapi;
