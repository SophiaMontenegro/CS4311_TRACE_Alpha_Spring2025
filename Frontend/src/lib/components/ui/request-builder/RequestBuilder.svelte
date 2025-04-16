<script>
  import { onMount } from 'svelte';
  import { enhance } from '$app/forms';
  import { createEventDispatcher } from 'svelte';

  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Textarea } from '$lib/components/ui/textarea';
  import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
  import { Label } from '$lib/components/ui/label';
  import { Card, CardContent } from '$lib/components/ui/card';
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
  import { validateHeaders } from '$lib/validation/validateHeaders';

  const dispatch = createEventDispatcher();

  // form state
  let method = 'GET';
  let targetUrl = '';
  let headers = '';
  let cookies = '';
  let requestBody = '';

  // derived / helper state
  let rawEnabled = false;
  let rawRequest = '';

  // enhance + persistence
  const STORAGE_KEY = 'httpTesterFormData';
  let customEnhance;
  let formEl;

onMount(() => {
	// restore cached form state
	const saved = localStorage.getItem(STORAGE_KEY);
	if (saved) {
		const s = JSON.parse(saved);
		method      = s.method      ?? 'GET';
		targetUrl   = s.targetUrl   ?? '';
		headers     = s.headers     ?? '';
		cookies     = s.cookies     ?? '';
		requestBody = s.requestBody ?? '';
	}

	/**
	 * The action returned by `enhance` will be passed straight to
	 * `use:enhance={callback}` in the <form>.  The callback receives
	 * `{ result }`, where `result` is a Promise<Response>.
	 */
	customEnhance = enhance(({ result }) => {
		result.then(async (res) => {
			// turn the streaming response into a plain object for the UI

      const headers = {};
      res.headers.forEach((value, key) => {
        headers[key] = value;
      });

			const detail = {
				status:     res.status,
				statusText: res.statusText,
				headers:    headers,   
				cookies:    {},                                        
				body:       await res.text(),
				time:       null,                                        
				size:       res.headers.get('content-length') ?? null
			};

			if (!res.ok) {
				detail.error = detail.statusText || 'Request failed';
			}

			dispatch('response', detail);
		});
	});
});

  /* ---------- helpers ---------- */

  function buildRawRequest() {
    try {
      const u = new URL(targetUrl);
      let raw = `${method} ${u.pathname || '/'} HTTP/1.1\n`;
      raw += `Accept: */*\n`;
      raw += `Host: ${u.host}\n`;
      if (method !== 'GET') raw += `Content-Type: application/json\n`;
      raw += `User-Agent: TRACE-system\n`;

      headers.split('\n').forEach((h) => {
        const trimmed = h.trim();
        if (trimmed) raw += trimmed + '\n';
      });

      if (cookies.trim()) raw += `Cookie: ${cookies}\n`;
      raw += `\n${requestBody}`;
      return raw;
    } catch {
      return '';
    }
  }

  function validateForm() {
    const errors = [];

    if (!targetUrl.trim()) {
      errors.push('Target URL is required.');
    } else if (!/^https?:\/\/[^\s]+$/.test(targetUrl.trim())) {
      errors.push('Target URL must start with http:// or https://');
    }

    const headerValidation = validateHeaders(headers);
    if (headerValidation.error) {
      errors.push(`Headers: ${headerValidation.message}`);
    }

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

  function saveToLocalStorage() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ method, targetUrl, headers, cookies, requestBody })
    );
  }

  /* ---------- event handlers ---------- */

  function handleSubmit(e) {
    const errors = validateForm();
    if (errors.length) {
      e.preventDefault();
      alert(errors.join('\n'));
      return;
    }
    saveToLocalStorage();
  }

  function handleKeydown(e) {
    if (e.ctrlKey && e.key === 'Enter' && formEl) {
      e.preventDefault();
      formEl.requestSubmit();
    }
  }

  /* ---------- reactive ---------- */
  $: rawRequest = buildRawRequest();
  $: rawEnabled = !!rawRequest;
</script>

<svelte:window on:keydown={handleKeydown} />

{#if customEnhance}
  <form
    bind:this={formEl}
    use:customEnhance
    on:submit={handleSubmit}
    class="h-full w-full"
  >
    <Card class="h-full w-full flex flex-col shadow-lg overflow-hidden">
      <CardContent class="flex-1 flex flex-col p-3">
        <h2 class="text-xl font-bold mb-4">Request Builder</h2>

        <div class="flex-1 flex flex-col overflow-hidden">
          <Tabs value={rawEnabled ? 'raw' : 'request'} class="flex-1 flex flex-col overflow-hidden">
            <TabsList class="border-b shrink-0">
              <TabsTrigger value="request">Request</TabsTrigger>
              <TabsTrigger value="headers">Headers</TabsTrigger>
              <TabsTrigger value="body">Body</TabsTrigger>
              {#if rawEnabled}
                <TabsTrigger value="raw">Raw</TabsTrigger>
              {/if}
            </TabsList>

            <!-- Request Tab -->
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

            <!-- Headers Tab -->
            <TabsContent value="headers" class="flex-1 overflow-auto p-4">
              <Label for="headers">Headers</Label>
              <Textarea
                id="headers"
                name="headers"
                bind:value={headers}
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

            <!-- Body Tab -->
            <TabsContent value="body" class="flex-1 overflow-auto p-4">
              <Label for="requestBody">Body</Label>
              <Textarea
                id="requestBody"
                name="requestBody"
                bind:value={requestBody}
                rows="8"
                disabled={method === 'GET'}
              />
            </TabsContent>

            <!-- Raw Tab -->
            <TabsContent value="raw" class="flex-1 overflow-auto p-4">
              <Label>Raw HTTP Request</Label>
              <Textarea rows="15" bind:value={rawRequest} />
            </TabsContent>
          </Tabs>
        </div>

        <div class="border-t p-4 flex justify-end">
          <Button type="submit" class="px-4 h-8">Send</Button>
        </div>
      </CardContent>
    </Card>
  </form>
{/if}
