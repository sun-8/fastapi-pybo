<script>
    export let error // 전달받은 오류
</script>

<!-- 오류의 detail 속성이 배열로 구성된 경우 : 필드 오류 - 해당 배열을 순회하며 필드명과 오류를 출력 -->
<!-- 오류의 detail 속성이 문자열인 경우 : 일반 오류 - 오류의 내용만 표시 -->
{#if typeof error.detail === 'string'}
    <div class="alert alert-danger" role="alert">
        <div>
            {error.detail}
        </div>
    </div>
{:else if typeof error.detail === 'object' && error.detail.length > 0}
    <div class="alert alert-danger" role="alert">
        {#each error.detail as err, i}
        <div>
            <!-- loc[1] = content -->
            <strong>{err.loc[1]}</strong> : {err.msg}
        </div>
        {/each}
    </div>
{/if}