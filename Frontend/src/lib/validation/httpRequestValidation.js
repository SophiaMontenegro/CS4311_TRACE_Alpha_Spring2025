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
  
  function normalizeUrlFromRequestTarget(requestTarget, headers) {
    let url = requestTarget.trim();
  
    if (/^[a-z][a-z0-9+.-]*:\/\//i.test(url)) {
      // Already absolute
    } else if (url.startsWith('/')) {
      const host = headers['Host'] || headers['host'];
      if (!host) throw new Error('Missing Host header for origin-form request');
      url = `https://${host}${url}`;
    } else {
      url = `https://${url.replace(/^[a-z]+:\/\//i, '')}`;
    }
  
    try {
      new URL(url);
    } catch {
      throw new Error(`Invalid URL: ${url}`);
    }
  
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


export function parseSetCookie(header) {
  if (!header) return {};

  const cookies = {};
  const cookieParts = Array.isArray(header) ? header : [header];

  for (const part of cookieParts) {
    const parts = part.split(';').map(p => p.trim());
    const [key, value] = parts[0].split('=');
    if (key && value) {
      cookies[key.trim()] = {
        value: value.trim(),
        attributes: parts.slice(1)
      };
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
