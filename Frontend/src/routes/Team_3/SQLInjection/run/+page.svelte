<script>
    import { onMount, onDestroy } from 'svelte';
    import { goto } from '$app/navigation';

    let analystInitials = '';
    let scanId = '';
    let progress = 30;
    let scanStatus = 'running';
    let statusMessage = 'Scanning...';

    let testingType = 'Error-based SQL Injection';
    let processedRequests = 0;
    let effectivePayloads = 0;
    let responseTime = '0.32s';

    let results = [
        { id: 1, parameter: 'id', method: 'GET', type: 'Integer', payload: "1' OR '1'='1", status: 'Success', length: 2345, vulnerability: 'High' },
        { id: 2, parameter: 'username', method: 'POST', type: 'String', payload: "admin' --", status: 'Error', length: 1240, vulnerability: 'Medium' },
        { id: 3, parameter: 'search', method: 'GET', type: 'String', payload: "1 UNION SELECT 1,2,3", status: 'Success', length: 3120, vulnerability: 'Critical' }
    ];

    let pollingInterval;

    function handleLogout() {
        localStorage.removeItem('analyst_id');
        localStorage.removeItem('analyst_initials');
        goto('/login');
    }

    function pauseScan() {
        if (confirm('Are you sure you want to pause the scan?')) {
            scanStatus = 'paused';
            statusMessage = 'Paused';
            clearInterval(pollingInterval);
        }
    }

    function resumeScan() {
        scanStatus = 'running';
        statusMessage = 'Scanning...';
        startPolling();
    }

    function stopScan() {
        if (confirm('Are you sure you want to stop the scan?')) {
            scanStatus = 'completed';
            statusMessage = 'Stopped by user';
            clearInterval(pollingInterval);
        }
    }

    function restartScan() {
        if (confirm('Restart scan and lose current progress?')) {
            progress = 0;
            processedRequests = 0;
            effectivePayloads = 0;
            scanStatus = 'running';
            statusMessage = 'Scanning...';
            startPolling();
        }
    }

    function modifySettings() {
        goto('/sqlmap');
    }

    function startPolling() {
        pollingInterval = setInterval(() => {
            if (scanStatus === 'running') {
                progress += Math.random() * 2;
                if (progress >= 100) {
                    progress = 100;
                    scanStatus = 'completed';
                    statusMessage = 'Scan completed';
                    clearInterval(pollingInterval);
                }

                processedRequests += Math.floor(Math.random() * 5) + 1;
                if (Math.random() > 0.7) {
                    effectivePayloads += 1;

                    if (Math.random() > 0.5 && results.length < 20) {
                        const payloads = [
                            "' OR 1=1 --", "admin' --", "1 UNION SELECT 1,2,3",
                            "1; DROP TABLE users --", "' OR '1'='1"
                        ];
                        const parameters = ['id', 'username', 'search', 'query', 'filter'];
                        const methods = ['GET', 'POST'];
                        const types = ['Integer', 'String', 'Boolean'];
                        const statuses = ['Success', 'Error', 'Timeout'];
                        const vulnerabilities = ['Low', 'Medium', 'High', 'Critical'];

                        results = [...results, {
                            id: results.length + 1,
                            parameter: parameters[Math.floor(Math.random() * parameters.length)],
                            method: methods[Math.floor(Math.random() * methods.length)],
                            type: types[Math.floor(Math.random() * types.length)],
                            payload: payloads[Math.floor(Math.random() * payloads.length)],
                            status: statuses[Math.floor(Math.random() * statuses.length)],
                            length: Math.floor(Math.random() * 5000) + 500,
                            vulnerability: vulnerabilities[Math.floor(Math.random() * vulnerabilities.length)]
                        }];
                    }
                }

                responseTime = (Math.random() * 0.5 + 0.1).toFixed(2) + 's';
            }
        }, 1000);
    }

    onMount(() => {
        analystInitials = localStorage.getItem('analyst_initials') || '';
        if (!analystInitials) goto('/login');
        const urlParams = new URLSearchParams(window.location.search);
        scanId = urlParams.get('id') || localStorage.getItem('current_scan_id') || 'test-scan-123';
        startPolling();
    });

    onDestroy(() => {
        clearInterval(pollingInterval);
    });
</script>

<div class="flex flex-col min-h-screen">
    <header class="bg-gray-100 dark:bg-gray-900 shadow p-4 flex justify-between items-center">
        <h1 class="text-xl font-bold text-primary">TRACE</h1>
        <div class="flex items-center gap-4">
            <span class="text-muted-foreground">Analyst: {analystInitials}</span>
            <button class="text-red-600 hover:underline text-sm" on:click={handleLogout}>Logout</button>
        </div>
    </header>

    <nav class="flex bg-background text-muted-foreground border-b p-2 space-x-4">
        <button on:click={() => goto('/dashboard')} class="hover:text-primary">Dashboard</button>
        <button class="text-primary font-semibold">SQL Injection</button>
        <button on:click={() => goto('/settings')} class="hover:text-primary">Settings</button>
    </nav>

    <div class="flex flex-1 overflow-hidden">
        <aside class="w-48 bg-gray-50 dark:bg-gray-800 p-4 border-r text-sm">
            <ul class="space-y-2">
                <li class="hover:text-primary cursor-pointer" on:click={() => goto('/sqlmap')}>Configuration</li>
                <li class="text-primary font-semibold">Running</li>
                <li class="text-muted-foreground">Reports</li>
            </ul>
        </aside>

        <main class="flex-1 p-6 overflow-y-auto">
            <h2 class="text-xl font-bold">SQL Injection</h2>
            <p class="text-muted-foreground mb-4">Running</p>

            <div class="bg-white dark:bg-gray-900 rounded-xl shadow p-4 space-y-6">
                <div class="flex justify-between items-center">
                    <div class="w-full">
                        <div class="flex justify-between mb-1">
                            <span class="text-sm font-medium">{Math.floor(progress)}%</span>
                            <span class="text-sm text-muted-foreground">{statusMessage}</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2.5">
                            <div class="bg-primary h-2.5 rounded-full" style="width: {progress}%"></div>
                        </div>
                    </div>

                    <div class="flex gap-2 ml-4">
                        {#if scanStatus === 'running'}
                            <button class="btn" on:click={pauseScan}>Pause</button>
                            <button class="btn" on:click={stopScan}>Stop</button>
                        {:else if scanStatus === 'paused'}
                            <button class="btn" on:click={resumeScan}>Resume</button>
                            <button class="btn" on:click={stopScan}>Stop</button>
                        {:else if scanStatus === 'completed'}
                            <button class="btn" on:click={restartScan}>Restart</button>
                        {/if}
                        <button class="btn" on:click={modifySettings}>Settings</button>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div class="p-2 bg-muted rounded-lg">
                        <div class="text-xs text-muted-foreground">Testing Type</div>
                        <div class="font-semibold text-sm">{testingType}</div>
                    </div>
                    <div class="p-2 bg-muted rounded-lg">
                        <div class="text-xs text-muted-foreground">Processed Requests</div>
                        <div class="font-semibold text-sm">{processedRequests}</div>
                    </div>
                    <div class="p-2 bg-muted rounded-lg">
                        <div class="text-xs text-muted-foreground">Effective Payloads</div>
                        <div class="font-semibold text-sm">{effectivePayloads}</div>
                    </div>
                    <div class="p-2 bg-muted rounded-lg">
                        <div class="text-xs text-muted-foreground">Response Time</div>
                        <div class="font-semibold text-sm">{responseTime}</div>
                    </div>
                </div>

                <div>
                    <h3 class="font-semibold text-lg mb-2">Injection Results</h3>
                    <div class="overflow-auto rounded-lg border">
                        <table class="w-full text-sm text-left">
                            <thead class="bg-muted text-muted-foreground">
                            <tr>
                                <th class="px-4 py-2">#</th>
                                <th class="px-4 py-2">Parameter</th>
                                <th class="px-4 py-2">Method</th>
                                <th class="px-4 py-2">Type</th>
                                <th class="px-4 py-2">Payload</th>
                                <th class="px-4 py-2">Status</th>
                                <th class="px-4 py-2">Length</th>
                                <th class="px-4 py-2">Vulnerability</th>
                            </tr>
                            </thead>
                            <tbody>
                            {#each results as result}
                                <tr class="border-t">
                                    <td class="px-4 py-2">{result.id}</td>
                                    <td class="px-4 py-2">{result.parameter}</td>
                                    <td class="px-4 py-2">{result.method}</td>
                                    <td class="px-4 py-2">{result.type}</td>
                                    <td class="px-4 py-2 font-mono text-xs">{result.payload}</td>
                                    <td class="px-4 py-2 {result.status === 'Error' ? 'text-red-500' : ''}">{result.status}</td>
                                    <td class="px-4 py-2">{result.length}</td>
                                    <td class="px-4 py-2 font-bold {result.vulnerability.toLowerCase()}">
                                        {result.vulnerability}
                                    </td>
                                </tr>
                            {/each}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    </div>
</div>
