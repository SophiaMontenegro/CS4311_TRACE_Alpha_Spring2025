export async function load({ fetch, url }) {
	const jobId = url.searchParams.get('jobId');  

	if (!jobId) {
		return {
			tableData: [],
			tableColumns: []
		};
	}

	console.log('[Fetcher] Fetching results for job:', jobId);

	try {
		const res = await fetch(`http://127.0.0.1:8000/api/ml/${jobId}/results`);
		const json = await res.json();
		return {
			tableData: json.results ?? [],
			tableColumns: [
				{ key: 'id', label: 'ID' },
				{ key: 'username', label: 'Username' },
				{ key: 'username_score', label: 'Username Score' },
				{ key: 'password', label: 'Password' },
				{ key: 'is_secure', label: 'Secure?' },
				{ key: 'password_evaluation', label: 'Evaluation' }
			]
		};
	} catch (e) {
		console.error('[Fetcher] Failed to load ML results:', e);
		return {
			tableData: [],
			tableColumns: []
		};
	}
}