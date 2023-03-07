// 스토어를 사용하여 변수의 값을 전역적으로 저장해 라우팅 되는 페이지에 상관없이 스토어에 저장된 변수를 사용
// ex) 3페이지의 어떤 게시글을 클릭 후 뒤로가기 버튼을 눌렀을 때 1페이지가 아닌 3페이지로 이동하도록

import { writable } from "svelte/store";

// writable의 초깃값을 0으로 설정
// export const page = writable(0)

// 스토어 변수를 사용했는데도 해결되지 않는 문제
// ex) 3페이지의 어떤 게시글을 클릭 후 새로고침 후 뒤로가기 버튼을 눌렀을 때 3페이지가 아닌 1페이지로 이동
//      브라우저에서 "새로고침"을 하는 순간 스토어 변수가 초기화 되기 때문
// 이러한 현상은 자바스크립트의 location.href 또는 a태그를 통해 링크를 호출할 경우에도 발생

// key : 이름, initValue : 초기값
// localStorage를 사용하여 지속성을 가짐.
// localStorage에 해당 이름의 값이 이미 존재하는 경우 초기값 대신 기존의 값으로 스토어를 생성하여 리턴.
// localStorage에 저장하는 값은 항상 문자열로 유지하기 위해 저장할 때는 JSON.stringify를 사용하고 읽을 때는 JSON.parse를 사용.
const persist_storage = (key, initValue) => {
    const storedValueStr = localStorage.getItem(key)
    const store = writable(storedValueStr != null ? JSON.parse(storedValueStr) : initValue)
    // 스토어에 저장된 값이 변경될 때 실행되는 콜백함수
    store.subscribe((val) => {
        localStorage.setItem(key, JSON.stringify(val))
    })
    return store
}

export const page = persist_storage("page", 0)
export const keyword = persist_storage("keyword", "")

// 다음의 3가지 로그인 정보는 브라우저를 새로고침 하더라도 유지
// 액세스 토큰은 로그인이 필요한 API를 호출할때 Header 항목에 그 값을 대입하여 호출
// 로그인 성공을 하면 is_login에 true라는 값을 설정
export const access_token = persist_storage("access_token", "") // 액세스 토큰
export const username = persist_storage("username", "") // 사용자명
export const is_login = persist_storage("is_login", false) // 로그인 여부