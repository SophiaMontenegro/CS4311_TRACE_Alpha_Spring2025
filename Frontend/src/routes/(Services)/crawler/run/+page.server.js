export async function load({ fetch, url }) {
	const jobId = url.searchParams.get('jobId');  

	if (!jobId) {
		return {
			tableData: [],
			tableColumns: []
		};
	}

	try {
		const apiBaseURL = localStorage.getItem('apiBaseURL');
		if (!apiBaseURL) throw new Error('API Base URL is not set!');
		const res = await fetch(`${apiBaseURL}/api/crawler/${jobId}/results`);
		const json = await res.json();
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
