<script>
  import { push } from "svelte-spa-router";
  import fastapi from "../lib/api";
  import Error from "../components/Error.svelte"
  import { access_token, username, is_login } from "../lib/store"


    let error = {detail:[]}
    // username은 다른 용도로 사용할 예정이기 때문에 사용자 이름에 대응되는 바인딩 변수로 username이 아닌 login_username을 사용
    // 로그인을 성공하면 username 항목을 리턴받는데 이 값을 스토어 변수 username에 저장하여 사용할 것
    let login_username = "",
        login_password = ""

    function login(event) {
        event.preventDefault()
        let url = "/api/user/login"
        let params = {
            username: login_username,
            password: login_password
        }
        // operation 값으로 'post' 대신 'login'을 전달
        fastapi('login', url, params, 
            (json) => {
                $access_token = json.access_token
                $username = json.username
                $is_login = true
                push("/")
            }, (json_err) => {error = json_err})
    }
</script>

<div class="container">
    <h5 class="my-3 border-bottom pb-2">로그인</h5>
    <Error error={error} />
    <form method="post">
        <div class="mb-3">
            <label for="username">사용자 이름</label>
            <input type="text" class="form-control" id="username" bind:value={login_username}>
        </div>
        <div class="mb-3">
            <label for="password">비밀번호</label>
            <input type="password" class="form-control" id="password" bind:value={login_password}>
        </div>
        <button type="submit" class="btn btn-primary" on:click={login}>로그인</button>
    </form>
</div>