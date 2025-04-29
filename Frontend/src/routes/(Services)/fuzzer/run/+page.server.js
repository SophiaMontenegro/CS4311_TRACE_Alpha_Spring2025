import { getApiBaseURL } from '$lib/utils/apiBaseURL';

export async function load({ fetch, url }) {
	let jobId = url.searchParams.get('jobId');

	if (!jobId) {
		return {
			tableData: [],
			tableColumns: []
		};
	}

	try {
		const apiBaseURL = getApiBaseURL();
		const res = await fetch(`${apiBaseURL}/api/fuzzer/${jobId}/results`);
		const json = await res.json();
		return {
			tableData: json.results ?? [],
			tableColumns: [
				{ key: 'id', label: 'ID' },
				{ key: 'response', label: 'Response' },
				{ key: 'url', label: 'URL' },
				{ key: 'payload', label: 'Payload' },
				{ key: 'length', label: 'Length (chars)' },
				{ key: 'snippet', label: 'Snippet' },
				{ key: 'error', label: 'Error' }
			]
		};
	} catch (e) {
		console.error('Failed to load fuzzer results:', e);
		return {
			tableData: [],
			tableColumns: []
		};
	}
}
