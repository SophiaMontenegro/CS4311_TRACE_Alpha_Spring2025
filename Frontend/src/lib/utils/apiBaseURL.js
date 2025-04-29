export function getApiBaseURL() {
	const apiBaseURL = localStorage.getItem('apiBaseURL');
	if (!apiBaseURL) {
		throw new Error('API Base URL is not set!');
	}
	return apiBaseURL;
}
