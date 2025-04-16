export async function load({ fetch, url }) {
	let jobId = url.searchParams.get('jobId');

	if (!jobId) {
		return {
			tableData: [],
			tableColumns: []
		};
	}

	console.log('[Fetcher] Fetching results for job:', jobId);

	try {
		const res = await fetch(`http://127.0.0.1:8000/api/fuzzer/${jobId}/results`);
		const json = await res.json();
		console.log('[DataTable] Results:', json.results);
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
