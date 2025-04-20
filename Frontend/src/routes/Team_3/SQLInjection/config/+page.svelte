<script>
    import { onMount } from 'svelte';
    import { goto } from '$app/navigation';
    import { Button } from '$lib/components/ui/button/index.js';
    import { Label } from '$lib/components/ui/label/index.js';
    import { Switch } from '$lib/components/ui/switch/index.js';
    import StepIndicator from '$lib/components/ui/progressStep/ProgressStep.svelte';
    import FormField from '$lib/components/ui/form/FormField.svelte';

    let analystInitials = '';

    let formData = {
        targetUrl: '',
        targetPort: '',
        injectableParams: '',
        customFlags: '',
        dbUser: '',
        dbPass: '',
        enumLevel: '1',
        timeout: '30',
        additional: '',
        dbEnum: false
    };



    let progress = 0;
    let message = '';
    let history = [];

    let fieldErrors = {};

    const API_BASE_URL = 'http://127.0.0.1:8000';


    const inputFields = [
        {
            id: 'targetUrl',
            label: 'Target URL',
            placeholder: 'http://example.com',
            tooltip: 'Enter the target URL to test for SQL injection vulnerabilities',
            required: true,
            advanced: false
        },
        {
            id: 'targetPort',
            label: 'Target Port',
            placeholder: '80',
            tooltip: 'Enter the port number of the target',
            required: true,
            advanced: false
        },
        {
            id: 'injectableParams',
            label: 'Injectable Parameters',
            placeholder: 'id',
            tooltip: 'Comma-separated parameter names to test (optional)',
            required: false,
            advanced: false
        },
        {
            id: 'customFlags',
            label: 'Custom Flags',
            placeholder: '--random-agent',
            tooltip: 'Optional additional SQLMap flags',
            required: false,
            advanced: true
        },
        {
            id: 'dbUser',
            label: 'DB Username',
            placeholder: 'admin',
            tooltip: 'Optional: Database username if known',
            required: false,
            advanced: true
        },
        {
            id: 'dbPass',
            label: 'DB Password',
            placeholder: 'password123',
            tooltip: 'Optional: Database password if known',
            required: false,
            advanced: true
        },
        {
            id: 'enumLevel',
            label: 'Enumeration Level',
            placeholder: '1',
            tooltip: 'Enumeration level (1-5)',
            required: false,
            advanced: true
        },
        {
            id: 'timeout',
            label: 'Timeout',
            placeholder: '30',
            tooltip: 'Timeout in seconds',
            required: false,
            advanced: true
        },
        {
            id: 'additional',
            label: 'Additional Flags',
            placeholder: '',
            tooltip: 'Any other custom SQLMap flags',
            required: false,
            advanced: true
        }
    ];

    function handleInputChange(id, value) {
        formData[id] = value;
        validateField(id, value);
    }

    function validateField(id, value) {
        if (id === 'targetUrl' && !value) {
            fieldErrors[id] = { error: true, message: 'Target URL is required' };
        } else if (id === 'targetPort') {
            if (!value) {
                fieldErrors[id] = { error: true, message: 'Target Port is required' };
            } else if (!/^\d+$/.test(value)) {
                fieldErrors[id] = { error: true, message: 'Port must be numeric' };
            } else {
                fieldErrors[id] = null;
            }
        } else if (id === 'enumLevel') {
            if (value && !/^[1-5]$/.test(value)) {
                fieldErrors[id] = { error: true, message: 'Level must be 1-5' };
            } else {
                fieldErrors[id] = null;
            }
        } else if (id === 'timeout') {
            if (value && !/^\d+$/.test(value)) {
                fieldErrors[id] = { error: true, message: 'Timeout must be numeric' };
            } else {
                fieldErrors[id] = null;
            }
        } else {
            fieldErrors[id] = null;
        }
    }



    async function runScan(event) {
        event.preventDefault();

        // Validate all required fields
        for (const field of inputFields) {
            validateField(field.id, formData[field.id]);
        }

        const hasErrors = Object.values(fieldErrors).some((e) => e?.error);
        if (hasErrors) {
            message = 'Please fix the errors before running the scan';
            return;
        }

        message = 'Starting scan...';
        progress = 10;

        try {
            let flags = formData.customFlags || '';
            if (formData.dbUser) flags += ` --dbuser=${formData.dbUser}`;
            if (formData.dbPass) flags += ` --dbpass=${formData.dbPass}`;
            if (formData.enumLevel) flags += ` --level=${formData.enumLevel}`;
            if (formData.timeout) flags += ` --timeout=${formData.timeout}`;
            if (formData.dbEnum) flags += ` --dbs`;
            if (formData.additional) flags += ` ${formData.additional}`;

            const res = await fetch(`${API_BASE_URL}/sqlmap/scan`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    url: formData.targetUrl,
                    port: formData.targetPort,
                    params: formData.injectableParams,
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

    function handleLogout() {
        localStorage.removeItem('analyst_id');
        localStorage.removeItem('analyst_initials');
        goto('/login'); // path is not correct fix later
    }

    onMount(() => {
        analystInitials = localStorage.getItem('analyst_initials') || '';
        if (!analystInitials) goto('/login');
        fetchHistory();
    });
</script>

<svelte:head>
    <title>SQL Injection Configuration | TRACE</title>
</svelte:head>

<div class="injection-config">
    <div class="title-section">
        <div class="title">SQL Injection Configuration</div>
        <StepIndicator status="config" />
    </div>

    <form on:submit={runScan} class="input-container">

        {#each inputFields as field}
            <FormField
                    {field}
                    value={formData[field.id]}
                    error={fieldErrors[field.id]?.error}
                    errorText={fieldErrors[field.id]?.message}
                    onInput={(e) => handleInputChange(field.id, e.target.value)}
            />
        {/each}

        <div class="flex items-center space-x-2 mt-4">
            <Label for="dbEnum">Enable DB Enumeration</Label>
            <Switch id="dbEnum" bind:checked={formData.dbEnum} />
        </div>

        <Button type="submit" class="w-96 mt-4">Submit</Button>
    </form>
</div>
<style>
    .injection-config {
        display: flex;
        margin-left: 4.5rem;
        height: 100vh;
        flex-direction: column;
        justify-content: space-around;
    }
    .title-section {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        max-height: fit-content;
        padding-right: 3rem;
    }
    .title {
        font-size: 2rem;
        font-style: normal;
        font-weight: 600;
        padding-left: 3rem;
        padding-top: 3rem;
    }
    .input-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100%;
        height: 100%;
        gap: 1rem;
    }
</style>
