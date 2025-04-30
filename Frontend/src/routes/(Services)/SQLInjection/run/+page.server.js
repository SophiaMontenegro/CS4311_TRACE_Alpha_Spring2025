import { getApiBaseURL } from '$lib/utils/apiBaseURL';

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
		const apiBaseURL = getApiBaseURL();
		const res = await fetch(`${apiBaseURL}/api/sqlinjection/${jobId}/results`);
		const json = await res.json();
		console.log('[DataTable] Results:', json.results);
		return {
			tableData: json.results ?? [],
			tableColumns: [
				{ key: 'id', label: 'ID' },
				{ key: 'type', label: 'Type' },
				{ key: 'details', label: 'Details' },
				{ key: 'parameter', label: 'Parameter' },
				{ key: 'vulnerabilityType', label: 'Vulnerability Type' },
				{ key: 'severity', label: 'Severity' },
				{ key: 'status', label: 'Status' }
			]
		};
	} catch (e) {
		console.error('Failed to load SQL injection results:', e);
		return {
			tableData: [],
			tableColumns: []
		};
	}
}