export const actions = {
	default: async ({ request }) => {
		const formData = await request.formData();

		const targetUrl = formData.get('targetUrl')?.toString() || '';
		const method = formData.get('method')?.toString() || 'GET';
		const header = formData.get('header')?.toString() || '';
		const cookies = formData.get('cookies')?.toString() || '';
		const proxy = formData.get('proxy')?.toString() || '';
		const requestBody = formData.get('requestBody')?.toString() || '';

		if (!targetUrl) {
			return {
				status: 400,
				statusText: 'Bad Request',
				time: 0,
				size: 0,
				headers: {},
				cookies: {},
				body: 'Target URL is required'
			};
		}

		try {
			const startTime = Date.now();

			// Prepare headers
			const headers = {};
			if (header) {
				const parts = header.split(':').map(part => part.trim());
				if (parts[0] && parts[1]) {
					headers[parts[0]] = parts[1];
				} else {
					headers['Content-Type'] = header;
				}
			}

			// Prepare cookies
			if (cookies) {
				headers['Cookie'] = cookies;
			}

			// Prepare fetch options
			const fetchOptions = {
				method,
				headers,
				redirect: 'follow'
			};

			// Add body for POST/PUT requests if provided
			if ((method === 'POST' || method === 'PUT') && requestBody) {
				fetchOptions.body = requestBody;
			}

			// Dynamically import proxy agents if a proxy is specified
			if (proxy) {
				const isHttps = proxy.startsWith('https://');
				if (isHttps) {
					const { HttpsProxyAgent } = await import('https-proxy-agent');
					fetchOptions.agent = new HttpsProxyAgent(proxy);
				} else {
					const { HttpProxyAgent } = await import('http-proxy-agent');
					fetchOptions.agent = new HttpProxyAgent(proxy);
				}
			}

			// Make the request
			const response = await fetch(targetUrl, fetchOptions);
			const endTime = Date.now();
			const responseTime = endTime - startTime;

			// Get response body
			const responseBody = await response.text();
			const responseSize = new TextEncoder().encode(responseBody).length;

			// Extract headers
			const responseHeaders = {};
			response.headers.forEach((value, key) => {
				responseHeaders[key] = value;
			});

			// Extract cookies from "set-cookie" header
			const responseCookies = {};
			const cookieHeader = response.headers.get('set-cookie');
			if (cookieHeader) {
				cookieHeader.split(',').forEach(cookie => {
					const [cookiePart] = cookie.split(';');
					const [cookieKey, cookieValue] = cookiePart.split('=').map(part => part.trim());
					if (cookieKey && cookieValue) {
						responseCookies[cookieKey] = cookieValue;
					}
				});
			}

			return {
				status: response.status,
				statusText: response.statusText,
				time: responseTime,
				size: responseSize,
				headers: responseHeaders,
				cookies: responseCookies,
				body: responseBody
			};
		} catch (error) {
			console.error('Error making request:', error);
			return {
				status: 500,
				statusText: 'Internal Server Error',
				time: 0,
				size: 0,
				headers: {},
				cookies: {},
				body: `Error: ${error instanceof Error ? error.message : String(error)}`
			};
		}
	}
};