<!-- 네비게이션 바 : 메인 페이지로 돌아갈 수 있는 장치가 없는 것이 불편하여 추가. 모든 화면 위쪽에 고정되어있는 부트스트랩 컴포넌트-->
<script>
  import { link } from "svelte-spa-router"
  import { is_login, access_token, username, page, keyword } from "../lib/store"
  import { Confirm } from 'svelte-confirm'
</script>

<!-- 네비게이션 바 -->
<nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom">
  <div class="container-fluid">
    <!-- 스토어에 페이지 번호가 저장되어 있어 첫번째 페이지로 이동되지 않는 것 방지-->
    <a use:link class="navbar-brand" href="/" on:click={() => {$keyword = '', $page = 0}}>테스트게시판</a>
    <button
      class="navbar-toggler"
      type="button"
      data-bs-toggle="collapse"
      data-bs-target="#navbarSupportedContent"
      aria-controls="navbarSupportedContent"
      aria-expanded="false"
      aria-label="Toggle navigation"
    >
      <span class="navbar-toggler-icon" />
    </button>
    <div class="collapse navbar-collapse" id="navbarSupportedContent">
      <ul class="navbar-nav me-auto mb-2 mb-lg-0">
        {#if $is_login} <!-- 로그인 한 경우 -->
            <li class="nav-item">
                <!-- 로그아웃은 스토어 변수를 초기화 -->
                <a use:link href="/user-login" class="nav-link" on:click={() => {
                    $access_token = '' 
                    $username = '' 
                    $is_login = false
                }}>로그아웃 ({$username})</a>
            </li>
        {:else} <!-- 로그인 안 한 경우 -->
            <li class="nav-item">
                <a use:link class="nav-link" href="/user-create">회원가입</a>
            </li>
            <li class="nav-item">
                <a use:link class="nav-link" href="/user-login">로그인</a>
            </li>
        {/if}
      </ul>
    </div>
  </div>
</nav>