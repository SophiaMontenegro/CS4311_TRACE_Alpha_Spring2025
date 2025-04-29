// src/routes/(Services)/http-tester/+page.server.js
import { fail } from '@sveltejs/kit';
import {
  parseRawRequest,
  parseSetCookie,
  validateBodySize,
  parseHeaderString
} from '$lib/validation/httpRequestValidation.js';

export const actions = {
  default: async ({ request }) => {
    console.log('[Server] Action triggered');

    // 1) Pull out the form data
    const formData = await request.formData();
    const mode     = formData.get('mode')?.toString() || 'request';

    let method;
    let relativeUrl;
    let body;
    let headers   = {};
    let targetUrl;

    // 2) Parse raw vs structured form
    if (mode === 'raw') {
      const raw    = formData.get('rawRequest')?.toString() || '';
      const parsed = parseRawRequest(raw);
      method        = parsed.method.toUpperCase();
      targetUrl     = parsed.url;
      headers       = parsed.headers;
      body          = parsed.body;

      const bodyError = validateBodySize(body);
      if (bodyError) {
        // 413 Payload Too Large
        return fail(413, { error: bodyError.error ?? 'Body too large' });
      }

      try {
        const u = new URL(targetUrl);
        relativeUrl = u.pathname + u.search;
      } catch {
        // malformed URL in raw text
        return fail(400, { error: 'Invalid raw URL format' });
      }
    } else {
      targetUrl = formData.get('targetUrl')?.toString() || '';
      method    = formData.get('method')?.toString().toUpperCase() || 'GET';
      const headersRaw   = formData.get('headers')?.toString() || '';
      body                = formData.get('requestBody')?.toString() || '';

      const bodyError = validateBodySize(body);
      if (bodyError) {
        return fail(413, { error: bodyError.error ?? 'Body too large' });
      }

      // ensure protocol
      if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(targetUrl)) {
        targetUrl = `https://${targetUrl}`;
      }

      try {
        const parsed = new URL(targetUrl);
        relativeUrl = parsed.pathname + parsed.search;
      } catch {
        return fail(400, { error: 'Invalid URL format' });
      }

      // parse headers JSON or fallback to header‐string parser
      try {
        headers = JSON.parse(headersRaw);
      } catch {
        headers = parseHeaderString(headersRaw);
      }
    }

    // 3) Build and send the proxy payload
    const proxyPayload = {
      target: targetUrl,
      request: {
        method,
        url:    relativeUrl,
        headers,
        body:   method === 'GET' ? null : body
      }
    };

    let proxyRes;
    try {
      proxyRes = await fetch('http://127.0.0.1:8000/api/http/send', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(proxyPayload)
      });
    } catch (err) {
      // network failure talking to proxy
      return fail(502, { error: 'Cannot reach proxy server' });
    }

    // 4) Parse proxy JSON (or fail)
    let data;
    try {
      data = await proxyRes.json();
    } catch {
      const text = await proxyRes.text();
      return fail(502, {
        error: `Non-JSON response from proxy: ${text.slice(0, 100)}…`
      });
    }

    // 5) If the proxy itself returned an error field, bubble it up as 502
    if (data.error) {
      return fail(502, { error: data.error });
    }

    // 6) Success — build cookie map and return plain object
    const setCookieHeader = data.headers?.['set-cookie'] || data.headers?.['Set-Cookie'];
    const parsedCookies = parseSetCookie(setCookieHeader);
    
    return {
      success:     true,
      status_code: data.status_code   || proxyRes.status,
      statusText:  data.statusText    || proxyRes.statusText,
      headers:     data.headers       || {},
      cookies:     parsedCookies,
      body:        data.body          || '',
      time:        data.time   ?? null,
      size:        data.size   ?? null,
      version:     data.version        || '2'
    };
  }
};
