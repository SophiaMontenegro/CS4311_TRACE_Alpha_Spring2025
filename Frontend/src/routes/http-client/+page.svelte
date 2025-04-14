<script>
  import RequestBuilder from './RequestBuilder.svelte';
  import ResponsePanel from './ResponsePanel.svelte';

  let response = null;
  let hideCodes = [];
  let showOnlyCodes = [];

  function parseHeaders(str) {
    if (!str) return undefined;

    try {
      return JSON.parse(str);
    } catch {
      // fallback to simple line-by-line headers
    }

    const obj = {};
    str.split(/\r?\n/).forEach((line) => {
      const idx = line.indexOf(':');
      if (idx > -1) {
        const key = line.slice(0, idx).trim();
        const val = line.slice(idx + 1).trim();
        if (key) obj[key] = val;
      }
    });

    return Object.keys(obj).length ? obj : undefined;
  }

  async function handleSend(e) {
    const req = e.detail;

    hideCodes = req.hideCodes;
    showOnlyCodes = req.showOnlyCodes;

    if (!req.targetUrl) {
      response = { error: 'Missing target URL.' };
      return;
    }

    const start = performance.now();

    try {
      const res = await fetch(req.targetUrl, {
        method: req.method,
        headers: parseHeaders(req.headers),
        body: req.method === 'GET' ? undefined : req.requestBody
      });

      const bodyText = await res.text();

      response = {
        status: res.status,
        statusText: res.statusText,
        headers: Object.fromEntries(res.headers.entries()),
        cookies: (() => {
          const raw = res.headers.get('set-cookie');
          if (!raw) return {};
          const [pair] = raw.split(';');
          const [k, v] = pair.split('=');
          return { [k]: v };
        })(),
        body: bodyText,
        time: Math.round(performance.now() - start),
        size: Number(res.headers.get('content-length')) || bodyText.length
      };
    } catch (err) {
      response = {
        error: err.message,
        time: Math.round(performance.now() - start)
      };
    }
  }
</script>

<div class="flex justify-center items-center w-full h-screen">
  <div class="flex gap-4 w-full max-w-6xl h-[65vh]">
    <div class="w-1/2 h-full">
      <RequestBuilder on:send={handleSend} />
    </div>
    <div class="w-1/2 h-full">
      <ResponsePanel {response} {hideCodes} {showOnlyCodes} />
    </div>
  </div>
</div>
  
