export function load() {
  return {
    tools: [
      { name: 'Crawler', route: '/crawler/config' },
      { name: 'Fuzzer', route: '/fuzzer/config' },
      { name: 'Brute Force', route: '/bruteForce/config' },
      { name: 'Intruder', route: '/intruder' },
      { name: 'HTTP Tester', route: '/http-tester' },
      { name: 'SQL Injector', route: '/SQLInjection/config' }
    ]
  };
}
