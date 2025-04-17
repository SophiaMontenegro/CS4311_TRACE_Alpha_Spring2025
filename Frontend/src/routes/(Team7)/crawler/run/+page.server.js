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
		const res = await fetch(`http://127.0.0.1:8000/api/crawler/${jobId}/results`);
		const json = await res.json();
    console.log('[DataTable] Results:', json.results);
		return {
			tableData: json.results ?? [],
			tableColumns: [
        { key: 'id', label: 'ID' },
				{ key: 'url', label: 'URL'},
				{ key: 'parentUrl', label: 'Parent URL' },
				{ key: 'title', label: 'Title' },
				{ key: 'wordCount', label: 'Word Count' },
				{ key: 'charCount', label: 'Character Count' },
				{ key: 'linksFound', label: 'Links Found' },
				{ key: 'error', label: 'Error' }
			]
		};
	} catch (e) {
		console.error('Failed to load crawler results:', e);
		return {
			tableData: [],
			tableColumns: []
		};
	}
}
