export function load({ url }) {
	const projectName = url.searchParams.get('project');

	return {
		projectName,
		tools: [
			{ name: 'Crawler', route: '/crawler/config' },
			{ name: 'Fuzzer', route: '/fuzzer/config' },
			{ name: 'Brute Force', route: '/bruteForce/config' },
			{ name: 'HTTP Tester', route: '/http-tester' },
			{ name: 'Intruder', route: '/intruder' }
		]
	};
}
