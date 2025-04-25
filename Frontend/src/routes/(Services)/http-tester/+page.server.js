import { json } from '@sveltejs/kit';
import {
  parseRawRequest,
  parseSetCookie,
  validateBodySize,
  parseHeaderString
} from '$lib/validation/httpRequestValidation.js';

export const actions = {
  default: async ({ request }) => {
    console.log('[Server] Action triggered');

    try {
      const formData = await request.formData();
      const mode = formData.get('mode')?.toString() || 'request';

      let method, url, body;
      let headers = {};
      let targetUrl;

      if (mode === 'raw') {
        const raw = formData.get('rawRequest')?.toString() || '';
        const parsed = parseRawRequest(raw);
        method = parsed.method.toUpperCase();
        targetUrl = parsed.url;
        headers = parsed.headers;
        body = parsed.body;

        const bodyError = validateBodySize(body);
        if (bodyError) return json(bodyError, { status: 413 });

        const u = new URL(targetUrl);
        url = u.pathname + u.search;

      } else {
        targetUrl = formData.get('targetUrl')?.toString() || '';
        method = formData.get('method')?.toString().toUpperCase() || 'GET';
        const headersRaw = formData.get('headers')?.toString() || '';
        body = formData.get('requestBody')?.toString() || '';

        const bodyError = validateBodySize(body);
        if (bodyError) return json(bodyError, { status: 413 });

        if (!/^[a-z][a-z0-9+.-]*:\/\//i.test(targetUrl)) {
          targetUrl = `https://${targetUrl}`;
        }

        try {
          const parsed = new URL(targetUrl);
          url = parsed.pathname + parsed.search;
        } catch {
          return json({ error: 'Invalid URL format' }, { status: 400 });
        }

        try {
          headers = JSON.parse(headersRaw);
        } catch {
          headers = parseHeaderString(headersRaw);
        }
      }

      const proxyPayload = {
        target: targetUrl,
        request: {
          method,
          url,
          headers,
          body: method === 'GET' ? null : body
        }
      };

      const res = await fetch('http://127.0.0.1:8000/api/http/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(proxyPayload)
      });

      let data;
      try {
        data = await res.json();
      } catch {
        const text = await res.text();
        return json(
          { error: `Non-JSON response from proxy: ${text.slice(0, 100)}...` },
          { status: 502 }
        );
      }

      const parsedCookies = parseSetCookie(data.headers?.['Set-Cookie']);

      return {
        success: true,
        status_code: data.status_code || res.status,
        statusText: data.statusText || res.statusText,
        headers: data.headers || {},
        cookies: parsedCookies,
        body: data.body || '',
        time: data.time || null,
        size: data.size || null,
        version: data.version || '2'
      };

    } catch (error) {
      console.error('[Server] Action error:', error);
      return json(
        { error: error.message || 'Internal Server Error' },
        { status: 500 }
      );
    }
  }
};
