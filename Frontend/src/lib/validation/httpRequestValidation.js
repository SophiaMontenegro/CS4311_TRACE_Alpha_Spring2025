export function validateHeaders(rawHeaderString) {
    if (!rawHeaderString?.trim()) return { error: false, message: '' };
  
    const lines = rawHeaderString.split(/\r?\n/);
    const invalidLines = lines.filter(line => {
      const trimmed = line.trim();
      if (!trimmed) return false;
      const [key, ...rest] = trimmed.split(':');
      return !key || !rest.length || !rest.join(':').trim();
    });
  
    if (invalidLines.length > 0) {
      return {
        error: true,
        message: `Header lines must be in "Key: Value" format:\n${invalidLines.join('\n')}`
      };
    }
  
    return { error: false, message: '' };
  }
  
  export function parseRawRequest(raw) {
    if (typeof raw !== 'string') throw new TypeError('Raw request must be a string');
  
    const lines = raw.split(/\r?\n/);
    if (lines.length === 0) throw new Error('Empty raw request');
  
    const requestLine = lines.shift().trim();
    const [method, requestTarget, httpVersion] = requestLine.split(' ');
    if (!method || !requestTarget || !httpVersion) {
      throw new Error(`Invalid request line: ${requestLine}`);
    }
  
    const headers = {};
    let line;
    while ((line = lines.shift()) !== undefined) {
      if (!line.trim()) break;
      const [key, ...rest] = line.split(':');
      if (key && rest.length > 0) {
        headers[key.trim()] = rest.join(':').trim();
      }
    }
  
    const body = lines.join('\n').trim();
    const url = normalizeUrlFromRequestTarget(requestTarget, headers);
  
    return { method, url, headers, body };
  }
  

export function normalizeUrlFromRequestTarget(requestTarget, headers = {}) {
  let url = requestTarget.trim();


  if (/^[a-z][a-z0-9+.-]*:\/\//i.test(url)) {
    new URL(url);            // validate
    return url;
  }

  // Helper for case-insensitive header lookup
  const getHeader = (name) =>
    headers[name] ?? headers[name.toLowerCase()] ?? headers[name.toUpperCase()];


  if (url.startsWith('/')) {
    const host = getHeader('Host');
    if (!host) throw new Error('Missing Host header for origin-form request');

    // Prefer explicit proto from common proxy headers
    const forwarded = getHeader('X-Forwarded-Proto');
    const scheme =
      forwarded?.split(',')[0].trim() ||               // take first value
      /:443$/.test(host) ? 'https' :                   // port hints
      /:80$/.test(host)  ? 'http'  :
      'http';                                          // default fallback

    url = `${scheme}://${host}${url}`;
    new URL(url);
    return url;
  }

  const schemeGuess = /:443$/.test(url) ? 'https' : 'http';
  url = `${schemeGuess}://${url.replace(/^[a-z]+:\/\//i, '')}`;
  new URL(url);
  return url;
}


  // httpRequestValidation.js

export function validateRawRequestFormat(rawRequest) {
  const firstLine = rawRequest.split('\n', 1)[0]?.trim() || '';
  if (!/^([A-Z]+) \S+ HTTP\/1\.1$/.test(firstLine)) {
    return {
      error: true,
      message: 'Raw request must start with “METHOD /path HTTP/1.1”.'
    };
  }

  return { error: false, message: '' };
}


export function validateForm({
  activeTab,
  targetUrl,
  headers,
  cookies,
  requestBody,
  rawRequest,
  method
}) {
  const errors = [];

  if (activeTab === 'raw') {
    const rawValidation = validateRawRequestFormat(rawRequest);
    if (rawValidation.error) errors.push(rawValidation.message);
  } else {
    if (!targetUrl?.trim()) {
      errors.push('Target URL is required.');
    }

    const headerValidation = validateHeaders(headers);
    if (headerValidation.error) {
      errors.push(`Headers: ${headerValidation.message}`);
    }

    if (
      cookies?.trim() &&
      !/^[^=]+=[^;]+(?:;\s*[^=]+=[^;]+)*$/.test(cookies.trim())
    ) {
      errors.push('Cookies must be in key=value format, separated by semicolons.');
    }

    if (method !== 'GET' && requestBody?.trim()) {
      try {
        JSON.parse(requestBody);
      } catch {
        errors.push('Request body must be valid JSON.');
      }
    }
  }

  return errors;
}


export function parseSetCookie(setCookieHeader) {
  const cookies = {};

  if (!setCookieHeader) return cookies;

  const cookieStrings = Array.isArray(setCookieHeader) ? setCookieHeader : [setCookieHeader];

  for (const cookieStr of cookieStrings) {
    const parts = cookieStr.split(';')[0]; 
    const [name, value] = parts.split('=');
    if (name && value !== undefined) {
      cookies[name.trim()] = value.trim();
    }
  }

  return cookies;
}



export function validateBodySize(body, maxSize = 10000) {
  if (body?.length > maxSize) {
    return { error: 'Request body too large' };
  }
  return null;
}

export function parseHeaderString(str) {
  const headers = {};
  str.split(/\r?\n/).forEach(line => {
    const [key, ...rest] = line.split(':');
    if (key && rest.length > 0) {
      headers[key.trim()] = rest.join(':').trim();
    }
  });
  return headers;
}
