<script>
	import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
	import { Badge } from '$lib/components/ui/badge';
	import { Card, CardContent } from '$lib/components/ui/card';
	import Spinner from '$lib/components/ui/spinner/Spinner.svelte';

	export let isLoading = false;
	export let response = null;
	export let hideCodes = [];
	export let showOnlyCodes = [];

	let activeTab = 'preview';

	function getContentType(headers) {
		if (!headers) return '';
		const type = headers['Content-Type'] || headers['content-type'];
		return type?.toLowerCase() || '';
	}

	function formatBody(body, headers) {
		if (!body || typeof body !== 'string') return '';

		const contentType = getContentType(headers);

		// JSON formatting
		if (contentType.includes('application/json')) {
			try {
				return JSON.stringify(JSON.parse(body), null, 2);
			} catch {
				return body;
			}
		}

		// HTML formatting with DOCTYPE if present
		if (contentType.includes('text/html')) {
			try {
				const doctypeMatch = body.match(/<!doctype[^>]*>/i);
				const doctype = doctypeMatch ? doctypeMatch[0] + '\n' : '';

				const parser = new DOMParser();
				const doc = parser.parseFromString(body, 'text/html');

				if (!doc.body || !doc.body.childNodes.length) return body;

				const prettyBody = prettyPrintHTML(doc.body, 0).trim();
				return doctype + prettyBody;
			} catch {
				return body;
			}
		}

		// Fallback for everything else (e.g. text/plain, XML, etc.)
		return body;
	}

	function prettyPrintHTML(node, level) {
		const indent = '  '.repeat(level);
		let result = '';
		for (let child of node.childNodes) {
			if (child.nodeType === Node.TEXT_NODE) {
				const text = child.textContent.trim();
				if (text) result += `${indent}${text}\n`;
			} else if (child.nodeType === Node.ELEMENT_NODE) {
				const tag = child.tagName.toLowerCase();
				const attrs = [...child.attributes].map((a) => `${a.name}="${a.value}"`).join(' ');
				const open = attrs ? `<${tag} ${attrs}>` : `<${tag}>`;
				result += `${indent}${open}\n`;
				result += prettyPrintHTML(child, level + 1);
				result += `${indent}</${tag}>\n`;
			}
		}
		return result;
	}

	function getStatusColor(status) {
		if (status >= 200 && status < 300) return 'bg-[var(--success)]';
		if (status >= 300 && status < 500) return 'bg-[var(--warning)]';
		return 'bg-[var(--error)]';
	}

	function shouldShow(status) {
		const s = String(status);
		if (hideCodes.includes(s)) return false;
		if (showOnlyCodes.length && !showOnlyCodes.includes(s)) return false;
		return true;
	}

	// Build full response string
	$: fullHttpResponse = response
		? [
				`HTTP/${response.version ?? '1.1'} ${response.status} ${response.statusText}`,
				...Object.entries(response.headers || {}).map(([k, v]) => `${k}: ${v}`),
				'',
				response.body?.trimStart() ?? ''
			].join('\n')
		: '';
</script>

<Card class="flex h-full w-full flex-col border-[var(--border)] bg-[var(--card)] shadow-lg">
	<CardContent class="flex flex-1 flex-col gap-6 overflow-hidden p-6">
		<h2 class="text-xl font-bold text-[var(--primary)]">Response</h2>

		{#if isLoading}
			<div class="flex flex-1 items-center justify-center">
				<Spinner size="lg" />
			</div>
		{:else if response?.error}
			<div class="bg-[var(--error)]/10 rounded-lg p-4 text-[var(--error)]">
				<strong>Error:</strong>
				{response.error}
			</div>
		{:else if response && shouldShow(response.status)}
			<div class="flex items-center space-x-4">
				<Badge class={getStatusColor(response.status)}>
					{response.status}
					{response.statusText}
				</Badge>
				<span class="text-sm text-[var(--secondary)]">{response.time}ms</span>
				<span class="text-sm text-[var(--secondary)]">{response.size} bytes</span>
			</div>

			<Tabs bind:value={activeTab} class="flex flex-1 flex-col overflow-hidden">
				<TabsList class="shrink-0 border-b border-[var(--border)]">
					<TabsTrigger value="preview" class="flex-1">Preview</TabsTrigger>
					<TabsTrigger value="headers" class="flex-1">Headers</TabsTrigger>
					<TabsTrigger value="cookies" class="flex-1">Cookies</TabsTrigger>
					<TabsTrigger value="raw" class="flex-1">Raw</TabsTrigger>
				</TabsList>

				<TabsContent value="preview" class="flex-1 overflow-auto p-4">
					<pre
						class="h-full overflow-auto whitespace-pre-wrap rounded bg-[var(--muted)] p-4 font-mono text-sm">
{`HTTP/${response.version ?? '1.1'} ${response.status} ${response.statusText}
${Object.entries(response.headers || {})
	.map(([k, v]) => `${k}: ${v}`)
	.join('\n')}

${formatBody(response.body, response.headers)}`}
					</pre>
				</TabsContent>

				<TabsContent value="headers" class="flex-1 space-y-2 overflow-auto p-4">
					{#if response.headers && Object.keys(response.headers).length}
						{#each Object.entries(response.headers) as [key, value]}
							<div class="flex">
								<span class="min-w-[150px] font-semibold text-[var(--primary)]">{key}:</span>
								<span class="text-[var(--foreground)]">{value}</span>
							</div>
						{/each}
					{:else}
						<p class="text-[var(--muted)]">No headers found</p>
					{/if}
				</TabsContent>

				<TabsContent value="cookies" class="flex-1 space-y-2 overflow-auto p-4">
					{#if response.cookies && Object.keys(response.cookies).length}
						{#each Object.entries(response.cookies) as [key, value]}
							<div class="flex">
								<span class="min-w-[150px] font-semibold text-[var(--primary)]">{key}:</span>
								<span class="text-[var(--foreground)]">{value}</span>
							</div>
						{/each}
					{:else}
						<p class="text-[var(--muted)]">No cookies found</p>
					{/if}
				</TabsContent>

				<TabsContent value="raw" class="flex-1 overflow-auto p-4">
					<pre
						class="h-full overflow-auto whitespace-pre-wrap rounded bg-[var(--muted)] p-4 font-mono text-sm">
{fullHttpResponse}
					</pre>
				</TabsContent>
			</Tabs>
		{:else}
			<div class="flex flex-1 items-center justify-center text-[var(--muted)]">
				{#if response}
					Response filtered by status-code settings
				{:else}
					Send a request to see the response
				{/if}
			</div>
		{/if}
	</CardContent>
</Card>
