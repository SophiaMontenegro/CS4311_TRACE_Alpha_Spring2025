<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Input } from '$lib/components/ui/input/index.js';
    import { Label } from '$lib/components/ui/label/index.js';
    import { Checkbox } from '$lib/components/ui/checkbox/index.js';
    import { Card, CardContent } from '$lib/components/ui/card';

    let analystInitials = '';

    let targetUrl = '';
    let targetPort = '';
    let injectableParams = '';
    let customFlags = '';

    let dbUser = '';
    let dbPass = '';
    let enumLevel = '1';
    let timeout = '30';
    let additional = '';
    let dbEnum = false;

    let touched = {
        targetUrl: false,
        targetPort: false,
        enumLevel: false,
        timeout: false
    };

    let errors = {
        targetUrl: '',
        targetPort: '',
        enumLevel: '',
        timeout: ''
    };

    let tooltips = {
        targetUrl: 'Enter the target URL to test for SQL injection vulnerabilities',
        targetPort: 'Enter the port number of the target',
        dbUser: 'Optional: Database username if known',
        dbPass: 'Optional: Database password if known',
        enumLevel: 'Enumeration level (1-5)',
        timeout: 'Timeout in seconds',
        additional: 'Additional SQLMap parameters'
    };

    let progress = 0;
    let message = '';
    let history = [];

    const API_BASE_URL = 'http://127.0.0.1:8000';

    function handleBlur(field) {
        touched[field] = true;
        validate(field);
    }

    function validate(field) {
        if (field === 'targetUrl') {
            if (!targetUrl) {
                errors.targetUrl = 'URL is required';
            } else {
                errors.targetUrl = '';
            }
        } else if (field === 'targetPort') {
            if (!targetPort) {
                errors.targetPort = 'Port is required';
            } else if (!/^\d+$/.test(targetPort)) {
                errors.targetPort = 'Port must be a number';
            } else {
                errors.targetPort = '';
            }
        } else if (field === 'enumLevel') {
            if (enumLevel && !/^[1-5]$/.test(enumLevel)) {
                errors.enumLevel = 'Level must be 1-5';
            } else {
                errors.enumLevel = '';
            }
        } else if (field === 'timeout') {
            if (timeout && !/^\d+$/.test(timeout)) {
                errors.timeout = 'Must be a number';
            } else {
                errors.timeout = '';
            }
        }
    }

    function handleLogout() {
        localStorage.removeItem('analyst_id');
        localStorage.removeItem('analyst_initials');
        goto('/login'); // path is not correct fix later
    }

    async function runScan(event) {
        event.preventDefault();
        touched.targetUrl = true;
        touched.targetPort = true;
        validate('targetUrl');
        validate('targetPort');
        validate('enumLevel');
        validate('timeout');

        if (errors.targetUrl || errors.targetPort || errors.enumLevel || errors.timeout) {
            message = 'Please fix the errors before running the scan';
            return;
        }

        message = 'Starting scan...';
        progress = 10;

        try {
            let flags = customFlags || '';
            if (dbUser) flags += ` --dbuser=${dbUser}`;
            if (dbPass) flags += ` --dbpass=${dbPass}`;
            if (enumLevel) flags += ` --level=${enumLevel}`;
            if (timeout) flags += ` --timeout=${timeout}`;
            if (dbEnum) flags += ` --dbs`;
            if (additional) flags += ` ${additional}`;

            const res = await fetch(`${API_BASE_URL}/sqlmap/scan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    url: targetUrl,
                    port: targetPort,
                    params: injectableParams,
                    custom_flags: flags.trim()
                })
            });

            if (!res.ok) throw new Error('Failed to start scan');

            const data = await res.json();
            const scanId = data.scan_id;
            localStorage.setItem('current_scan_id', scanId);
            goto(`/sqlmap/running?id=${scanId}`);
        } catch (error) {
            console.error('Error starting scan:', error);
            message = `Error: ${error.message}`;
            progress = 0;
        }
    }

    async function fetchHistory() {
        try {
            const res = await fetch(`${API_BASE_URL}/sqlmap/history`);
            if (res.ok) {
                const data = await res.json();
                history = data.history || [];
            }
        } catch (error) {
            console.error('Error fetching history:', error);
        }
    }

    onMount(() => {
        analystInitials = localStorage.getItem('analyst_initials') || '';
        if (!analystInitials) goto('/login');
        fetchHistory();
    });
</script>

<div class="relative min-h-screen p-4">

    <!-- Top right logout section -->
    <div class="absolute top-4 right-4 flex items-center space-x-4">
        <span class="text-sm">Analyst: {analystInitials}</span>
        <Button on:click={handleLogout} variant="destructive">Logout</Button>
    </div>

    <!-- Main page content goes here -->
    <div class="mt-20">
        <Card class="p-6 max-w-3xl mx-auto mt-8">
            <CardContent class="space-y-4">
                <div class="flex justify-between items-center">
                    <h2 class="text-xl font-semibold">SQL Injection Configuration</h2>

                </div>

                <form class="space-y-4" on:submit={runScan}>
                    <div>
                        <Label for="url">Target URL</Label>
                        <Input id="url" type="text" placeholder="http://10.0.2.5/vuln.php" bind:value={targetUrl} on:blur={() => handleBlur('targetUrl')} />
                        {#if touched.targetUrl && errors.targetUrl}<p class="text-red-500 text-sm">{errors.targetUrl}</p>{/if}
                    </div>

                    <div>
                        <Label for="port">Target Port</Label>
                        <Input id="port" type="text" placeholder="80" bind:value={targetPort} on:blur={() => handleBlur('targetPort')} />
                        {#if touched.targetPort && errors.targetPort}<p class="text-red-500 text-sm">{errors.targetPort}</p>{/if}
                    </div>

                    <div>
                        <Label for="params">Injectable Parameters</Label>
                        <Input id="params" type="text" placeholder="id=1" bind:value={injectableParams} />
                    </div>

                    <div>
                        <Label for="dbUser">Database Username</Label>
                        <Input id="dbUser" type="text" placeholder="Optional" bind:value={dbUser} />
                    </div>

                    <div>
                        <Label for="dbPass">Database Password</Label>
                        <Input id="dbPass" type="password" placeholder="Optional" bind:value={dbPass} />
                    </div>

                    <div>
                        <Label for="enumLevel">Enumeration Level</Label>
                        <Input id="enumLevel" type="text" placeholder="1" bind:value={enumLevel} on:blur={() => handleBlur('enumLevel')} />
                        {#if touched.enumLevel && errors.enumLevel}<p class="text-red-500 text-sm">{errors.enumLevel}</p>{/if}
                    </div>

                    <div>
                        <Label for="timeout">Timeout</Label>
                        <Input id="timeout" type="text" placeholder="30" bind:value={timeout} on:blur={() => handleBlur('timeout')} />
                        {#if touched.timeout && errors.timeout}<p class="text-red-500 text-sm">{errors.timeout}</p>{/if}
                    </div>

                    <div>
                        <Label for="additional">Additional Parameters</Label>
                        <Input id="additional" type="text" placeholder="--risk=3" bind:value={additional} />
                    </div>

                    <div class="flex items-center space-x-2">
                        <Checkbox id="dbEnum" bind:checked={dbEnum} />
                        <Label for="dbEnum">Enable DB Enumeration</Label>
                    </div>

                    <Button type="submit">Run Scan</Button>
                </form>
            </CardContent>
        </Card>

    </div>

</div>


