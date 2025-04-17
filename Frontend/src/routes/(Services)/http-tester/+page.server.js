import { json } from '@sveltejs/kit';

/**
 * Parses the `Set-Cookie` header into an object of key-value pairs.
 */
function parseSetCookie(header) {
	const cookies = {};
	if (!header) return cookies;

	const cookieParts = Array.isArray(header) ? header : [header];
	for (const part of cookieParts) {
		const [kv] = part.split(';');
		const [key, value] = kv.split('=');
		if (key && value) {
			cookies[key.trim()] = value.trim();
		}
	}
	return cookies;
}

export const actions = {
	default: async ({ request }) => {
		console.log('[Server] Action triggered');

		try {
			const formData = await request.formData();

			let targetUrl = formData.get('targetUrl')?.toString() || '';
			const method = formData.get('method')?.toUpperCase() || 'GET';
			const headersRaw = formData.get('headers')?.toString() || '';
			const requestBody = formData.get('requestBody')?.toString() || '';

			console.log('[Server] Received form data:', {
				targetUrl,
				method,
				headersRaw,
				requestBody
			});

			if (!targetUrl) {
				return json({ error: 'Target URL is required' }, { status: 400 });
			}

			if (!/^https?:\/\//.test(targetUrl)) {
				targetUrl = `http://${targetUrl}`;
			}

			let parsedUrl;
			try {
				parsedUrl = new URL(targetUrl);
			} catch {
				console.warn('Invalid URL:', targetUrl);
				return json({ error: 'Invalid URL format' }, { status: 400 });
			}

			const headers = {};
			try {
				Object.assign(headers, JSON.parse(headersRaw));
			} catch {
				headersRaw.split(/\r?\n/).forEach((line) => {
					const [key, ...rest] = line.split(':');
					if (key && rest.length > 0) {
						headers[key.trim()] = rest.join(':').trim();
					}
				});
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

			console.log('Sending request to backend proxy:', proxyPayload);

			const res = await fetch('http://127.0.0.1:8000/api/http/send', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(proxyPayload)
			});

			const data = await res.json();

			const parsedCookies = parseSetCookie(data.headers?.['Set-Cookie']);
			const responsePayload = {
				status_code: data.status_code || res.status || 200,
				statusText: data.statusText || res.statusText || 'OK',
				headers: data.headers || {},
				cookies: parsedCookies,
				body: data.body || '',
				time: data.time || null,
				size: data.size || null
			};

			console.log('Returning to frontend:', responsePayload);
			return {
				success: true,
				...responsePayload
			};
		} catch (error) {
			console.error('Server action error:', error);
			return json({ error: error.message || 'Internal Server Error' }, { status: 500 });
		}
	}
};
