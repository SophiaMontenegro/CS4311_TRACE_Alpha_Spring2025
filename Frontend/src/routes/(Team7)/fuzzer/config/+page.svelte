<script>
	import { enhance, applyAction } from '$app/forms';
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { validateField } from '$lib/validation/fieldValidatorFactory.js';
	import { goto } from '$app/navigation';
	import { serviceStatus } from '$lib/stores/projectServiceStore';
	import { scanProgress, startScanProgress } from '$lib/stores/scanProgressStore.js';
	import StepIndicator from '$lib/components/ui/progressStep/ProgressStep.svelte';
	import FormField from '$lib/components/ui/form/FormField.svelte';
	import * as Accordion from '$lib/components/ui/accordion/index.js';
	import * as RadioGroup from '$lib/components/ui/radio-group/index.js';
	import { connectToFuzzerWebSocket } from '$lib/services/fuzzerSocket.js';

	let formData = {};
	let fieldErrors = {};
	let selectedFile = null;
	let httpMethod = 'GET';

	let inputFields = [
		{
			id: 'target-url',
			label: 'Target URL',
			type: 'text',
			placeholder: 'https://juice-shop.herokuapp.com',
			required: true,
			advanced: false,
			toolTip: 'The URL of the target application to be fuzzed'
		},
		{
			id: 'parameters',
			label: 'Parameters',
			type: 'text',
			placeholder: 'username, password',
			required: true,
			advanced: false,
			toolTip: 'Comma-separated list of parameters to be fuzzed (username, password, etc.)'
		},
		{
			id: 'headers',
			label: 'Headers',
			type: 'text',
			placeholder: 'User-Agent: Mozilla/5.0',
			required: false,
			advanced: true,
			toolTip: 'Custom headers to be included in the request'
		},
		{
			id: 'proxy',
			label: 'Proxy URL',
			type: 'text',
			placeholder: 'http://127.0.0.1:8080',
			required: false,
			advanced: true,
			toolTip: 'Proxy URL for the fuzzer to use'
		},
		{
			id: 'body-template',
			label: 'Body Template',
			type: 'text',
			placeholder: 'username: payload, password: payload',
			required: false,
			advanced: true,
			toolTip: 'Template for the body of POST requests'
		},
		{
			id: 'cookies',
			label: 'Cookies',
			type: 'text',
			placeholder: 'sessionId=abc123',
			required: false,
			advanced: true,
			toolTip: 'Cookies to be included in the request'
		}
	];

	function handleInputChange(id, value) {
		if (id === 'wordlist') {
			selectedFile = value;
			fieldErrors.wordlist = validateField('wordlist', selectedFile);
		} else {
			formData[id] = value;
			const fieldResult = validateField(id, value);
			fieldErrors[id] = fieldResult;
		}
	}

	function validateAllFields() {
		let isValid = true;

		inputFields.forEach((field) => {
			const value = formData[field.id];
			const result = validateField(field.id, value);
			fieldErrors[field.id] = result;

			if (field.required && (!value || result.error)) {
				isValid = false;
			}
		});

		// Validate the wordlist file
		const fileResult = validateField('wordlist', selectedFile);
		fieldErrors.wordlist = fileResult;

		if (fileResult.error) {
			isValid = false;
		}

		return isValid;
	}

	const onSubmitHandler = () => {
		return async ({ result, update }) => {
			const isValid = validateAllFields();

			if (!isValid) {
				return;
			}

			if (result.type === 'success' && result.data?.success) {
				const jobId = result.data.job_id;

				if (!jobId) {
					console.error('Job ID missing from server response.');
					return;
				}

				localStorage.setItem('currentFuzzerJobId', jobId);

				setTimeout(() => {
					import('$lib/services/fuzzerSocket').then(({ connectToFuzzerWebSocket }) => {
						connectToFuzzerWebSocket(jobId);
					});
				}, 500);

				console.log('[Service Status]', $serviceStatus);
				console.log('[Scan Progress]', $scanProgress);

				goto('/fuzzer/run', { replaceState: true });
			} else {
				await update();
			}
		};
	};
</script>

<svelte:head>
	<title>Fuzzer Configuration | TRACE</title>
</svelte:head>

<div class="fuzzer-config">
	<div class="title-section">
		<div class="title">Fuzzer Configuration</div>
		<StepIndicator status="config" />
	</div>
	<form
		method="POST"
		enctype="multipart/form-data"
		use:enhance={onSubmitHandler}
		class="input-container"
	>
		{#each inputFields.filter((field) => !field.advanced) as field}
			<FormField
				{field}
				value={formData[field.id] || ''}
				error={fieldErrors[field.id]?.error || false}
				errorText={fieldErrors[field.id]?.message || ''}
				onInput={(e) => handleInputChange(field.id, e.target.value)}
				onBlur={() => handleInputChange(field.id, formData[field.id])}
			/>
		{/each}

		<FormField
			field={{
				id: 'wordlist',
				label: 'Wordlist',
				type: 'file',
				required: true,
				toolTip: 'Upload a .txt file containing payloads for the fuzzer'
			}}
			value={formData.wordlist || ''}
			error={fieldErrors.wordlist?.error || false}
			errorText={fieldErrors.wordlist?.message || ''}
			onInput={(e) => handleInputChange('wordlist', e.target.files?.[0] ?? null)}
			onBlur={() => handleInputChange('wordlist', selectedFile)}
		/>

		<Label for="HTTP-method" class="flex w-full max-w-96 gap-1 font-medium">
			HTTP Method<span class="text-red-500">*</span>
		</Label>

		<RadioGroup.Root bind:value={httpMethod} class="flex w-full max-w-96 flex-row gap-4">
			<div class="flex items-center space-x-2">
				<RadioGroup.Item value="GET" id="get" />
				<Label for="get">GET</Label>
			</div>
			<div class="flex items-center space-x-2">
				<RadioGroup.Item value="PUT" id="put" />
				<Label for="put">PUT</Label>
			</div>
			<div class="flex items-center space-x-2">
				<RadioGroup.Item value="POST" id="post" />
				<Label for="post">POST</Label>
			</div>
		</RadioGroup.Root>
		<!-- Hidden input to send the HTTP method to the server -->
		<input type="hidden" name="http-method" value={httpMethod} />

		<Accordion.Root type="single" class="w-96 max-w-full">
			<Accordion.Item value="item-1">
				<Accordion.Trigger>Advanced Settings</Accordion.Trigger>
				<Accordion.Content>
					{#each inputFields.filter((field) => field.advanced) as field}
						<FormField
							{field}
							value={formData[field.id] || ''}
							error={fieldErrors[field.id]?.error || false}
							errorText={fieldErrors[field.id]?.message || ''}
							onInput={(e) => handleInputChange(field.id, e.target.value)}
							onBlur={() => handleInputChange(field.id, formData[field.id])}
						/>
					{/each}
				</Accordion.Content>
			</Accordion.Item>
		</Accordion.Root>

		<div class="pb-8">
			<Button
				type="submit"
				variant="default"
				size="default"
				class="w-96"
				aria-label="Submit Form"
				title="Submit the form to start the fuzzer"
			>
				Submit
			</Button>
		</div>
	</form>
</div>

<style>
	.fuzzer-config {
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
