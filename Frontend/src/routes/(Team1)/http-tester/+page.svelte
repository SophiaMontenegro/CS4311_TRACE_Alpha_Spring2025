<script>
	import { enhance } from '$app/forms';
	import RequestBuilder from '$lib/components/ui/request-builder/RequestBuilder.svelte';
	import ResponsePanel from '$lib/components/ui/response-panel/ResponsePanel.svelte';

	let response = null;
	let hideCodes = [];
	let showOnlyCodes = [];

  async function handleResult({ result }) {
	const res = await result;

  if (result.type === 'failure') {
	response = { error: result.statusText };
	return;
}

const data = result.data;


  response = {
	status: data.status_code ?? 0, // fallback for safety
	statusText: data.statusText ?? 'OK',
	headers: data.headers ?? {},
	cookies: data.cookies ?? {},
	body: data.body ?? '',
	time: data.time ?? null,
	size: data.size ?? null
};

	console.log('🔁 Response received in UI:', response);
}


	// Adapter required by `use:enhance`
	const submitEnhance = (form) => {
		return async ({ result }) => handleResult({ result });
	};

	let formRef; // passed to child so Ctrl+Enter works
</script>

<form
  method="POST"
  use:enhance={submitEnhance}
  bind:this={formRef}
  class="flex justify-center items-center w-full h-screen"
>

	<div class="flex gap-4 w-full max-w-6xl h-[65vh]">
		<div class="w-1/2 h-full">
			<RequestBuilder {formRef} />
		</div>
		<div class="w-1/2 h-full">
			<ResponsePanel {response} {hideCodes} {showOnlyCodes} />
		</div>
	</div>
</form>
