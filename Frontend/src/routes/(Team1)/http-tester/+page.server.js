export const actions = {
	default: async ({ request }) => {
	  console.log('✅ [Server] Action triggered');
  
	  try {
		const formData = await request.formData();
  
		let targetUrl = formData.get('targetUrl')?.toString() || '';
		const method = formData.get('method')?.toUpperCase() || 'GET';
		const headersRaw = formData.get('headers')?.toString() || '';
		const requestBody = formData.get('requestBody')?.toString() || '';
  
		console.log('📥 [Server] Received form data:', {
		  targetUrl,
		  method,
		  headersRaw,
		  requestBody
		});
  
		if (!targetUrl) {
		  console.warn('⛔️ Missing target URL');
		  return {
			type: 'failure',
			status: 400,
			statusText: 'Target URL is required'
		  };
		}
  
		if (!/^https?:\/\//.test(targetUrl)) {
		  targetUrl = `http://${targetUrl}`;
		}
  
		let parsedUrl;
		try {
		  parsedUrl = new URL(targetUrl);
		} catch (err) {
		  console.warn('⛔️ Invalid URL:', targetUrl);
		  return {
			type: 'failure',
			status: 400,
			statusText: 'Invalid URL format'
		  };
		}
  
		const headers = {};
		try {
		  Object.assign(headers, JSON.parse(headersRaw));
		  console.log('📦 Parsed headers from JSON:', headers);
		} catch {
		  headersRaw.split(/\r?\n/).forEach(line => {
			const [key, ...rest] = line.split(':');
			if (key && rest.length > 0) {
			  headers[key.trim()] = rest.join(':').trim();
			}
		  });
		  console.log('📦 Parsed headers from text lines:', headers);
		}
  
		const proxyPayload = {
		  target: targetUrl,
		  request: {
			method,
			url: parsedUrl.pathname + parsedUrl.search,
			headers,
			body: method === 'GET' ? null : requestBody
		  }
		};
  
		console.log('🚀 Sending request to backend proxy:', proxyPayload);
  
		const res = await fetch('http://127.0.0.1:8000/api/http/send', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json'
		  },
		  body: JSON.stringify(proxyPayload)
		});
  
		const data = await res.json();
  
		console.log('✅ [Proxy Response]', data);
  
		const result = {
		  type: 'success',
		  data: {
			status_code: data.status_code || res.status || 200,
			statusText: data.statusText || res.statusText || 'OK',
			headers: data.headers || {},
			cookies: data.cookies || {},
			body: data.body || '',
			time: data.time || null,
			size: data.size || null
		  }
		};
  
		console.log('✅ Returning to frontend:', result);
		return result;
	  } catch (error) {
		console.error('🔥 Server action error:', error);
		return {
		  type: 'failure',
		  status: 500,
		  statusText: error.message || 'Internal Server Error'
		};
	  }
	}
  };
  