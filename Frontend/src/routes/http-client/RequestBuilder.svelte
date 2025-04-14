<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { Button } from '$lib/components/ui/button';
  import { Input } from '$lib/components/ui/input';
  import { Textarea } from '$lib/components/ui/textarea';
  import { RadioGroup, RadioGroupItem } from '$lib/components/ui/radio-group';
  import { Label } from '$lib/components/ui/label';
  import { Card, CardContent } from '$lib/components/ui/card';
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';

  let method = 'GET';
  let targetUrl = '';
  let headers = '';
  let cookies = '';
  let hideStatusCode = '';
  let showOnlyStatusCode = '';
  let proxy = '';
  let requestBody = '';
  let additionalParams = '';

  const STORAGE_KEY = 'httpTesterFormData';
  const dispatch = createEventDispatcher();

  function handleSubmit() {
    dispatch('send', {
      method,
      targetUrl,
      headers,
      cookies,
      requestBody,
      hideCodes: hideStatusCode.split(/\s*,\s*/).filter(Boolean),
      showOnlyCodes: showOnlyStatusCode.split(/\s*,\s*/).filter(Boolean),
      proxy,
      additionalParams
    });
    saveToLocalStorage();
  }

  function saveToLocalStorage() {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        method,
        targetUrl,
        headers,
        cookies,
        hideStatusCode,
        showOnlyStatusCode,
        proxy,
        requestBody,
        additionalParams
      })
    );
  }

  onMount(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (!saved) return;
    const data = JSON.parse(saved);
    method = data.method ?? 'GET';
    targetUrl = data.targetUrl ?? '';
    headers = data.headers ?? '';
    cookies = data.cookies ?? '';
    hideStatusCode = data.hideStatusCode ?? '';
    showOnlyStatusCode = data.showOnlyStatusCode ?? '';
    proxy = data.proxy ?? '';
    requestBody = data.requestBody ?? '';
    additionalParams = data.additionalParams ?? '';
  });
</script>

<svelte:window on:keydown={(e) => e.ctrlKey && e.key === 'Enter' && handleSubmit()} />

<Card class="bg-[var(--card)] border-[var(--border)] shadow-lg h-full w-full flex flex-col overflow-hidden">
  <CardContent class="p-3 flex-1 overflow-hidden text-sm space-y-4">
    <h2 class="text-xl font-bold text-[var(--primary)]">Request Builder</h2>

    <form on:submit|preventDefault={handleSubmit} class="flex-1 flex flex-col overflow-hidden">
      <Tabs value="request" class="flex-1 flex flex-col overflow-hidden">
        <TabsList class="border-b border-[var(--border)] shrink-0">
          <TabsTrigger value="request" class="flex-1">Request</TabsTrigger>
          <TabsTrigger value="headers" class="flex-1">Headers</TabsTrigger>
          <TabsTrigger value="body" class="flex-1">Body</TabsTrigger>
          <TabsTrigger value="advanced" class="flex-1">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="request" class="flex-1 overflow-auto p-4 space-y-4">
          <div class="space-y-1.5">
            <Label for="targetUrl">Target URL*</Label>
            <Input id="targetUrl" bind:value={targetUrl} required placeholder="https://example.com/api" />
          </div>

          <div class="space-y-1.5">
            <Label>HTTP Method</Label>
            <RadioGroup bind:value={method} name="method" class="flex space-x-4">
              {#each ['GET', 'POST', 'PUT'] as m}
                <div class="flex items-center space-x-2">
                  <RadioGroupItem value={m} id={m} />
                  <Label for={m}>{m}</Label>
                </div>
              {/each}
            </RadioGroup>
          </div>
        </TabsContent>

        <TabsContent value="headers" class="flex-1 overflow-auto p-4 space-y-4">
          <div class="space-y-1.5">
            <Label for="headers">Headers</Label>
            <Textarea id="headers" bind:value={headers} placeholder='Content-Type: application/json' />
          </div>
          <div class="space-y-1.5">
            <Label for="cookies">Cookies</Label>
            <Input id="cookies" bind:value={cookies} placeholder="csrf_token=123" />
          </div>
        </TabsContent>

        <TabsContent value="body" class="flex-1 overflow-auto p-4 space-y-4">
          <div class="space-y-1.5">
            <Label for="requestBody">Request Body</Label>
            <Textarea id="requestBody" bind:value={requestBody} rows="10" disabled={method === 'GET'} />
          </div>
        </TabsContent>

        <TabsContent value="advanced" class="flex-1 overflow-auto p-4 space-y-4">
          <div class="space-y-1.5">
            <Label for="hideStatusCode">Hide Status Code</Label>
            <Input id="hideStatusCode" bind:value={hideStatusCode} placeholder="403, etc." />
          </div>
          <div class="space-y-1.5">
            <Label for="showOnlyStatusCode">Show Only Status Code</Label>
            <Input id="showOnlyStatusCode" bind:value={showOnlyStatusCode} placeholder="200, 500, etc." />
          </div>
          <div class="space-y-1.5">
            <Label for="proxy">Proxy</Label>
            <Input id="proxy" bind:value={proxy} placeholder="https://proxy.example.com:3128" />
          </div>
          <div class="space-y-1.5">
            <Label for="additionalParams">Additional Parameters</Label>
            <Textarea id="additionalParams" bind:value={additionalParams} rows="3" />
          </div>
        </TabsContent>
      </Tabs>

      <div class="flex justify-end p-4 border-t border-[var(--border)]">
        <Button id="send-button" type="submit"
          class="h-8 px-4 text-sm bg-[var(--accent)] hover:bg-[var(--accent1)] text-[var(--accent-foreground)]">
          Send
        </Button>
      </div>
    </form>
  </CardContent>
</Card>