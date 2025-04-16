<script lang="ts">
    import { goto } from '$app/navigation';
    import { Input } from '$lib/components/ui/input';
    import { Button } from '$lib/components/ui/button';
    import { Card, CardContent, CardHeader, CardTitle } from '$lib/components/ui/card';
    import { Label } from '$lib/components/ui/label';

    let initials = '';
    let errorMessage = '';
    let isLoading = false;
    let debugInfo = '';
    let showRegisterForm = false;

    async function handleSubmit() {
        if (!initials.trim()) {
            errorMessage = 'Please enter your analyst initials';
            return;
        }

        isLoading = true;
        errorMessage = '';
        debugInfo = '';

        try {
            const response = await fetch(`http://127.0.0.1:8000/analysts/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ initials: initials.trim() }),
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('analyst_id', data.analyst_id);
                localStorage.setItem('analyst_initials', initials.trim());
                goto('/Team_3/dashboard');
            } else {
                debugInfo = JSON.stringify(data);
                errorMessage = data.detail || 'Invalid analyst initials';
            }
        } catch (error) {
            errorMessage = 'Connection error. Please try again.';
            debugInfo = error.toString();
        } finally {
            isLoading = false;
        }
    }

    function bypassLogin() {
        localStorage.setItem('analyst_id', 'test123');
        localStorage.setItem('analyst_initials', 'TEST');
        goto('/Team_3/dashboard');
    }

    function toggleRegisterForm() {
        showRegisterForm = !showRegisterForm;
        errorMessage = '';
        debugInfo = '';
    }

    async function registerAnalyst() {
        if (!initials.trim()) {
            errorMessage = 'Please enter your analyst initials';
            return;
        }

        isLoading = true;
        errorMessage = '';
        debugInfo = '';

        try {
            const response = await fetch(`http://127.0.0.1:8000/analysts/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    initials: initials.trim(),
                    name: initials.trim(),
                }),
            });

            const data = await response.json();

            if (response.ok) {
                localStorage.setItem('analyst_id', data.analyst_id);
                localStorage.setItem('analyst_initials', initials.trim());
                goto('/Team_3/dashboard');
            } else {
                debugInfo = JSON.stringify(data);
                errorMessage = data.detail || 'Registration failed';
            }
        } catch (error) {
            errorMessage = 'Connection error. Please try again.';
            debugInfo = error.toString();
        } finally {
            isLoading = false;
        }
    }
</script>

<div class="w-full min-h-screen flex items-center justify-center bg-muted px-4">
    <Card class="w-full max-w-md shadow-xl">
        <CardHeader>
            <CardTitle class="text-2xl text-center">
                TRACE {showRegisterForm ? 'Register' : 'Login'}
            </CardTitle>
        </CardHeader>
        <CardContent>
            <form on:submit|preventDefault={showRegisterForm ? registerAnalyst : handleSubmit} class="space-y-4">
                <div class="grid gap-2">
                    <Label for="initials">Analyst Initials</Label>
                    <Input
                            id="initials"
                            type="text"
                            bind:value={initials}
                            placeholder="Enter your initials (e.g., JD)"
                            maxlength="5"
                            required
                    />
                </div>

                {#if errorMessage}
                    <p class="text-sm text-red-500">{errorMessage}</p>
                {/if}

                {#if debugInfo}
                    <p class="text-xs text-gray-500">Debug: {debugInfo}</p>
                {/if}

                <Button type="submit" disabled={isLoading} class="w-full">
                    {#if isLoading}
                        {showRegisterForm ? 'Registering...' : 'Verifying...'}
                    {:else}
                        {showRegisterForm ? 'Register' : 'Login'}
                    {/if}
                </Button>

                <!-- Dev-only button -->
                {#if !showRegisterForm}
                    <Button type="button" variant="outline" on:click={bypassLogin} class="w-full">
                        Dev: Skip Login
                    </Button>
                {/if}
            </form>

            <div class="mt-4 text-center text-sm">
                {#if !showRegisterForm}
                    Analyst not found?
                    <button on:click={toggleRegisterForm} class="text-primary underline ml-1">Register here</button>
                {:else}
                    Already registered?
                    <button on:click={toggleRegisterForm} class="text-primary underline ml-1">Login here</button>
                {/if}
            </div>
        </CardContent>
    </Card>
</div>
