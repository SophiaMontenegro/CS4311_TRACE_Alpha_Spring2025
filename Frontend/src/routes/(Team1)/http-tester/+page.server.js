export const actions = {
	default: async ({ request }) => {
	  const formData = await request.formData();
  
	  let targetUrl = formData.get('targetUrl')?.toString() || '';
	  const method = formData.get('method')?.toUpperCase() || 'GET';
	  const headersRaw = formData.get('headers')?.toString() || '';
	  const requestBody = formData.get('requestBody')?.toString() || '';
  
	  if (!targetUrl) {
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
		return {
		  type: 'failure',
		  status: 400,
		  statusText: 'Invalid URL format'
		};
	  }
  
	  const headers = {};
	  try {
		Object.assign(headers, JSON.parse(headersRaw));
	  } catch {
		headersRaw.split(/\r?\n/).forEach(line => {
		  const [key, ...rest] = line.split(':');
		  if (key && rest.length > 0) {
			headers[key.trim()] = rest.join(':').trim();
		  }
		});
	  }
  
	  try {
		const res = await fetch('http://127.0.0.1:8000/api/http/send', {
		  method: 'POST',
		  headers: {
			'Content-Type': 'application/json'
		  },
		  body: JSON.stringify({
			target: targetUrl,
			request: {
			  method,
			  url: parsedUrl.pathname + parsedUrl.search,
			  headers,
			  body: method === 'GET' ? null : requestBody
			}
		  })
		});
  
		const data = await res.json();
  
		return {
		  type: 'success',
		  data
		};
	  } catch (error) {
		return {
		  type: 'failure',
		  status: 500,
		  statusText: error.message || 'Internal Server Error'
		};
	  }
	}
  };
  