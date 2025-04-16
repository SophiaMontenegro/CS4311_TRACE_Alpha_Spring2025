<script>
	import { enhance, applyAction } from '$app/forms';
	import { onMount } from 'svelte';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import { validateField } from '$lib/validation/fieldValidatorFactory.js';
	import { goto } from '$app/navigation';
	import { serviceStatus } from '$lib/stores/projectServiceStore';
	import StepIndicator from '$lib/components/ui/progressStep/ProgressStep.svelte';
	import FormField from '$lib/components/ui/form/FormField.svelte';
	import * as Accordion from '$lib/components/ui/accordion/index.js';
	import { connectToBruteForceWebSocket } from '$lib/services/bruteForceSocket.js';

	let formData = {};
	let fieldErrors = {};
	let selectedFile = null;

	let inputFields = [
		{
			id: 'target-url',
			label: 'Target URL',
			type: 'text',
			placeholder: 'https://juice-shop.herokuapp.com',
			required: true,
			advanced: false,
			toolTip: 'The URL of the domain being targeted.'
		},
		{
			id: 'attempt-limit',
			label: 'Attempt Limit',
			type: 'number',
			placeholder: '-1',
			required: true,
			advanced: false,
			toolTip: 'Maximum number of attempts per directory. Use -1 for unlimited.'
		},
		{
			id: 'top-level-directory',
			label: 'Top-Level Directory',
			type: 'text',
			placeholder: '/',
			required: false,
			advanced: true,
			toolTip: 'The directory path where bruteforce starts (defaults to root).'
		},
		{
			id: 'hide-status-codes',
			label: 'Hide Status Codes',
			type: 'text',
			placeholder: '403, 404',
			required: false,
			advanced: true,
			toolTip: 'Comma-separated list of HTTP status codes to hide in results.'
		},
		{
			id: 'show-status-codes',
			label: 'Show Only Status Codes',
			type: 'text',
			placeholder: '200, 500',
			required: false,
			advanced: true,
			toolTip: 'Comma-separated list of HTTP status codes to show exclusively.'
		},
		{
			id: 'filter-content-length',
			label: 'Filter by Content Length',
			type: 'text',
			placeholder: '>100, <500',
			required: false,
			advanced: true,
			toolTip: 'Optional content length filters (>100, <500).'
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

				localStorage.setItem('currentBruteForceJobId', jobId);

				setTimeout(() => {
					import('$lib/services/bruteForceSocket').then(({ connectToBruteForceWebSocket }) => {
						connectToBruteForceWebSocket(jobId);
					});
				}, 500);

				console.log('[Service Status]', $serviceStatus);
				goto('/bruteForce/run', { replaceState: true });
			} else {
				await update();
			}
		};
	};
</script>

<svelte:head>
	<title>bruteForce Configuration | TRACE</title>
</svelte:head>

<div class="bruteForce-config">
	<div class="title-section">
		<div class="title">Brute Force Configuration</div>
		<StepIndicator status="config" />
	</div>
	<form method="POST" enctype="multipart/form-data"
	use:enhance={onSubmitHandler} class="input-container">
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
				aria-label="Submit the form"
				title="Click to submit the form">Submit</Button
			>
		</div>
	</form>
</div>

<style>
	.bruteForce-config {
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
