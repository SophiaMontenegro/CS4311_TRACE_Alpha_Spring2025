<script>
  import RequestBuilder from '$lib/components/ui/request-builder/RequestBuilder.svelte';
  import ResponsePanel from '$lib/components/ui/response-panel/ResponsePanel.svelte';

  let response = null;
  let hideCodes = [];
  let showOnlyCodes = [];

  function handleResponse(event) {
    response = event.detail;
  }
</script>

<div class="flex justify-center items-center w-full h-screen">
  <div class="flex gap-4 w-full max-w-6xl h-[65vh]">
    <div class="w-1/2 h-full">
      <RequestBuilder on:response={handleResponse} />
    </div>
    <div class="w-1/2 h-full">
      <!-- <ResponsePanel {response} {hideCodes} {showOnlyCodes} /> -->
    </div>
  </div>
</div>
