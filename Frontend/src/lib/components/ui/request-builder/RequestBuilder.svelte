<script>
	import { onMount } from 'svelte';

	/* shadcn‑svelte UI bits */
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Textarea } from '$lib/components/ui/textarea';
	import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
	import { Label } from '$lib/components/ui/label';
	import { Card, CardContent } from '$lib/components/ui/card';
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { createEventDispatcher } from 'svelte';

	import { validateHeaders } from '$lib/validation/validateHeaders';

	export let formRef = null;
	export let activeTab;

	let method = 'GET';
	let targetUrl = '';
	let headers = '';
	let cookies = '';
	let requestBody = '';
	export let rawRequest = ''; // Now user-editable
	let rawEnabled = false;

	const STORAGE_KEY = 'httpTesterFormData';

	// Refresh raw request manually from parent
  export function refreshRawRequest() {
	console.log('🛠️ refreshRawRequest() called');
	console.log('method:', method);
	console.log('targetUrl:', targetUrl);
	console.log('headers:', headers);
	console.log('cookies:', cookies);
	console.log('requestBody:', requestBody);

	rawRequest = buildRawRequest();
	rawEnabled = !!rawRequest;

	console.log('🚀 rawRequest generated:\n', rawRequest);
}


function buildRawRequest() {
	try {
		let safeUrl = targetUrl.trim();
		if (!safeUrl.startsWith('http://') && !safeUrl.startsWith('https://')) {
			safeUrl = 'http://' + safeUrl;
		}

		const u = new URL(safeUrl);

		let raw = `${method} ${u.pathname || '/'} HTTP/1.1\n`;
		raw += 'Accept: */*\n';
		raw += `Host: ${u.host}\n`;
		if (method !== 'GET') raw += 'Content-Type: application/json\n';
		raw += 'User-Agent: TRACE-system\n';

		headers.split('\n').forEach((h) => {
			const trimmed = h.trim();
			if (trimmed) raw += trimmed + '\n';
		});

		if (cookies.trim()) raw += `Cookie: ${cookies}\n`;
		raw += `\n${requestBody}`;

		return raw;
	} catch (err) {
		console.warn('⚠️ Failed to build raw request:', err);
		return '';
	}
}


	onMount(() => {
		const saved = localStorage.getItem(STORAGE_KEY);
		if (saved) {
			try {
				const s = JSON.parse(saved);
				method = s.method ?? 'GET';
				targetUrl = s.targetUrl ?? '';
				headers = s.headers ?? '';
				cookies = s.cookies ?? '';
				requestBody = s.requestBody ?? '';
			} catch (e) {
				console.warn('[Storage] Failed to parse saved request:', e);
			}
		}
	});

	// Persist form fields to localStorage
	$: {
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem(
				STORAGE_KEY,
				JSON.stringify({ method, targetUrl, headers, cookies, requestBody })
			);
		}
	}

	let validationErrors = [];

	function validateForm() {
		const errors = [];

		if (!targetUrl.trim()) {
			errors.push('Target URL is required.');
		} else if (!/^https?:\/\/[^\s]+$/.test(targetUrl.trim())) {
			errors.push('Target URL must start with http:// or https://');
		}

		const headerValidation = validateHeaders(headers);
		if (headerValidation.error) errors.push(`Headers: ${headerValidation.message}`);

		if (
			cookies.trim() &&
			!/^[^=]+=[^;]+(?:;\s*[^=]+=[^;]+)*$/.test(cookies.trim())
		) {
			errors.push('Cookies must be in key=value format, separated by semicolons.');
		}

		if (method !== 'GET' && requestBody.trim()) {
			try {
				JSON.parse(requestBody);
			} catch {
				errors.push('Request body must be valid JSON.');
			}
		}

		return errors;
	}

	function onSubmit(e) {
		validationErrors = validateForm();
		if (validationErrors.length) {
			e.preventDefault();
		}
	}

	function handleKeydown(e) {
		if (e.ctrlKey && e.key === 'Enter' && formRef) {
			e.preventDefault();
			formRef.requestSubmit();
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

<Card class="h-full w-full flex flex-col shadow-lg overflow-hidden">
	<CardContent class="flex-1 flex flex-col p-3">
		<h2 class="text-xl font-bold mb-4">Request Builder</h2>

		{#if validationErrors.length}
			<div class="mb-3 rounded-lg bg-error/10 text-error p-3 space-y-1 text-sm">
				{#each validationErrors as err}
					<p>• {err}</p>
				{/each}
			</div>
		{/if}

		<div class="flex-1 flex flex-col overflow-hidden">
			<Tabs bind:value={activeTab} class="flex-1 flex flex-col overflow-hidden">
				<TabsList class="border-b shrink-0">
					<TabsTrigger value="request">Request</TabsTrigger>
					<TabsTrigger value="headers">Headers</TabsTrigger>
					<TabsTrigger value="body">Body</TabsTrigger>
					{#if rawRequest}
						<TabsTrigger value="raw">Raw</TabsTrigger>
					{/if}
				</TabsList>

				<!-- Request tab -->
				<TabsContent value="request" class="flex-1 overflow-auto p-4 space-y-4">
					<div>
						<Label for="targetUrl">URL*</Label>
						<Input id="targetUrl" name="targetUrl" bind:value={targetUrl} required />
					</div>

					<div>
						<Label>Method</Label>
						<RadioGroup bind:value={method} name="method" class="flex space-x-4">
							{#each ['GET', 'POST', 'PUT', 'DELETE'] as m}
								<div class="flex items-center space-x-2">
									<RadioGroupItem value={m} id={m} />
									<Label for={m}>{m}</Label>
								</div>
							{/each}
						</RadioGroup>
					</div>
				</TabsContent>

				<!-- Headers tab -->
				<TabsContent value="headers" class="flex-1 overflow-auto p-4">
					<Label for="headers">Headers</Label>
					<Textarea
						id="headers"
						name="headers"
						bind:value={headers}
						class="h-28"
						placeholder="Content-Type: application/json\nX-My-Header: abc123"
					/>

					<Label for="cookies" class="mt-4">Cookies</Label>
					<Input
						id="cookies"
						name="cookies"
						bind:value={cookies}
						placeholder="session=abc123"
					/>
				</TabsContent>

				<!-- Body tab -->
				<TabsContent value="body" class="flex-1 overflow-auto p-4">
					<Label for="requestBody">Body</Label>
					<Textarea
						id="requestBody"
						name="requestBody"
						class="h-40"
						bind:value={requestBody}
						disabled={method === 'GET'}
					/>
				</TabsContent>

				<!-- Raw tab -->
				<TabsContent value="raw" class="flex-1 overflow-auto p-4">
					<Label>Raw HTTP Request</Label>
					<Textarea rows="15" bind:value={rawRequest} class="font-mono" />
				</TabsContent>
			</Tabs>
		</div>

		<div class="border-t p-4 flex justify-end">
			<Button type="submit" class="px-4 h-8">Send</Button>
		</div>
	</CardContent>
</Card>
