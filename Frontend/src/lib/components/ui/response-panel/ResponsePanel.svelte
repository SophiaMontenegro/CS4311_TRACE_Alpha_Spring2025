<script>
  import { Tabs, TabsContent, TabsList, TabsTrigger } from '$lib/components/ui/tabs';
  import { Badge } from '$lib/components/ui/badge';
  import { Card, CardContent } from '$lib/components/ui/card';

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

  if (contentType.includes('application/json')) {
    try {
      const jsonObj = JSON.parse(body);
      return JSON.stringify(jsonObj, null, 2);
    } catch {
      return body;
    }
  }

  if (contentType.includes('text/html')) {
    const pretty = formatHTML(body);
    return pretty || body;
  }

  return body;
}



function formatHTML(html) {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    if (!doc.body || !doc.body.childNodes.length) return html; // fallback
    return prettyPrintHTML(doc.body, 0).trim();
  } catch {
    return html;
  }
}


  function prettyPrintHTML(node, indentLevel) {
    const indent = '  '.repeat(indentLevel);
    let result = '';

    for (let child of node.childNodes) {
      if (child.nodeType === Node.TEXT_NODE) {
        const text = child.textContent.trim();
        if (text) result += `${indent}${text}\n`;
      } else if (child.nodeType === Node.ELEMENT_NODE) {
        const tagName = child.tagName.toLowerCase();
        const attrs = [...child.attributes].map(attr => `${attr.name}="${attr.value}"`).join(' ');
        const openTag = attrs ? `<${tagName} ${attrs}>` : `<${tagName}>`;

        result += `${indent}${openTag}\n`;
        result += prettyPrintHTML(child, indentLevel + 1);
        result += `${indent}</${tagName}>\n`;
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
</script>

<Card class="bg-[var(--card)] border-[var(--border)] shadow-lg h-full flex flex-col w-full">
  <CardContent class="p-6 flex flex-col gap-6 flex-1 overflow-hidden">
    <h2 class="text-xl font-bold text-[var(--primary)]">Response</h2>

    {#if response && shouldShow(response.status)}
      <div class="flex items-center space-x-4">
        <Badge class={getStatusColor(response.status)}>
          {response.status} {response.statusText}
        </Badge>
        <span class="text-sm text-[var(--secondary)]">{response.time}ms</span>
        <span class="text-sm text-[var(--secondary)]">{response.size} bytes</span>
      </div>

      <Tabs bind:value={activeTab} class="flex-1 flex flex-col overflow-hidden">
        <TabsList class="border-b border-[var(--border)] shrink-0">
          <TabsTrigger value="preview"  class="flex-1">Preview</TabsTrigger>
          <TabsTrigger value="headers"  class="flex-1">Headers</TabsTrigger>
          <TabsTrigger value="cookies"  class="flex-1">Cookies</TabsTrigger>
          <TabsTrigger value="raw"      class="flex-1">Raw</TabsTrigger>
        </TabsList>

        <!-- Preview Tab: Pretty printed JSON or HTML -->
        <TabsContent value="preview" class="flex-1 overflow-auto p-4">
          <pre class="whitespace-pre-wrap font-mono text-sm bg-[var(--muted)] p-4 rounded overflow-auto h-full">
            {formatBody(response.body, response.headers)}
          </pre>
        </TabsContent>

        <!-- Headers Tab -->
        <TabsContent value="headers" class="flex-1 overflow-auto p-4 space-y-2">
          {#if response.headers && Object.keys(response.headers).length}
            {#each Object.entries(response.headers) as [key, value]}
              <div class="flex">
                <span class="font-semibold min-w-[150px] text-[var(--primary)]">{key}:</span>
                <span class="text-[var(--foreground)]">{value}</span>
              </div>
            {/each}
          {:else}
            <p class="text-[var(--muted)]">No headers found</p>
          {/if}
        </TabsContent>

        <!-- Cookies Tab -->
        <TabsContent value="cookies" class="flex-1 overflow-auto p-4 space-y-2">
          {#if response.cookies && Object.keys(response.cookies).length}
            {#each Object.entries(response.cookies) as [key, value]}
              <div class="flex">
                <span class="font-semibold min-w-[150px] text-[var(--primary)]">{key}:</span>
                <span class="text-[var(--foreground)]">{value}</span>
              </div>
            {/each}
          {:else}
            <p class="text-[var(--muted)]">No cookies found</p>
          {/if}
        </TabsContent>

        <!-- Raw Tab -->
        <TabsContent value="raw" class="flex-1 overflow-auto p-4">
          <pre class="whitespace-pre-wrap font-mono text-sm bg-[var(--muted)] p-4 rounded overflow-auto h-full">
{response.body}
          </pre>
        </TabsContent>
      </Tabs>
    {:else if response}
      <div class="flex-1 flex items-center justify-center text-[var(--muted)]">
        Response filtered by status‑code settings
      </div>
    {:else}
      <div class="flex-1 flex items-center justify-center text-[var(--muted)]">
        Send a request to see the response
      </div>
    {/if}
  </CardContent>
</Card>
