import { getApiBaseURL } from '$lib/utils/apiBaseURL';

export async function load({ fetch, url }) {
	let jobId = url.searchParams.get('jobId');

	if (!jobId) {
		return {
			tableData: [],
			tableColumns: []
		};
	}

	console.log('[Fetcher] Fetching brute force results for job:', jobId);

	try {
		const apiBaseURL = getApiBaseURL();
		const res = await fetch(`${apiBaseURL}/api/dbf/${jobId}/results`);
		const json = await res.json();
		return {
			tableData: json.results ?? [],
			tableColumns: [
				{ key: 'id', label: 'ID' },
				{ key: 'url', label: 'URL' },
				{ key: 'status', label: 'Status Code' },
				{ key: 'payload', label: 'Payload' },
				{ key: 'length', label: 'Length' },
				{ key: 'error', label: 'Error' }
			]
		};
	} catch (e) {
		console.error('Failed to load brute force results:', e);
		return {
			tableData: [],
			tableColumns: []
		};
	}
}
