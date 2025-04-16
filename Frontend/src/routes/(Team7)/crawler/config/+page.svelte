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
	import { connectToCrawlerWebSocket } from '$lib/services/crawlerSocket';

	let formData = {};
	let fieldErrors = {};

	let inputFields = [
		{
			id: 'target-url',
			label: 'Target URL',
			type: 'text',
			placeholder: 'https://juice-shop.herokuapp.com',
			required: true,
			advanced: false,
			toolTip: 'The URL of the target application to crawl.'
		},
		{
			id: 'depth',
			label: 'Crawl Depth',
			type: 'number',
			placeholder: '5',
			required: false,
			advanced: false,
			toolTip: 'The maximum depth of the crawl.'
		},
		{
			id: 'excluded-urls',
			label: 'Excluded URLs',
			type: 'text',
			placeholder: 'Comma-separated URLs to skip',
			required: false,
			advanced: true,
			toolTip: 'Comma-separated list of URLs to exclude from crawling.'
		},
		{
			id: 'crawl-date',
			label: 'Crawl Date',
			type: 'date',
			required: false,
			advanced: false,
			toolTip: 'The date to start the crawl from.'
		},
		{
			id: 'crawl-time',
			label: 'Crawl Time',
			type: 'time',
			required: false,
			advanced: false,
			toolTip: 'The time to start the crawl.'
		},
		{
			id: 'max-pages',
			label: 'Max Pages',
			type: 'number',
			placeholder: '50',
			required: false,
			advanced: true,
			toolTip: 'Maximum number of pages to crawl.'
		},
		{
			id: 'user-agent',
			label: 'User Agent',
			type: 'text',
			placeholder: 'https://juice-shop.herokuapp.com/drink/*',
			required: false,
			advanced: true,
			toolTip: 'User agent string to use for the crawl.'
		},
		{
			id: 'delay',
			label: 'Request Delay',
			type: 'number',
			placeholder: '1000',
			required: false,
			advanced: true,
			toolTip: 'Delay between requests in milliseconds.'
		},
		{
			id: 'proxy',
			label: 'Proxy URL',
			type: 'text',
			placeholder: 'http://127.0.0.1:8080',
			required: false,
			advanced: true,
			toolTip: 'Proxy URL to use for the crawl.'
		},
	];

	function handleInputChange(id, value) {
		formData[id] = value;
		const result = validateField(id, value);
		fieldErrors[id] = result;
	}

	function validateAllFields() {
		let isValid = true;

		inputFields.forEach((field) => {
			const result = validateField(field.id, formData[field.id]);
			fieldErrors[field.id] = result;

			if (field.required && (!formData[field.id] || result.error)) {
				isValid = false;
			}
		});

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

				localStorage.setItem('currentCrawlerJobId', jobId);

				setTimeout(() => {
					import('$lib/services/crawlerSocket').then(({ connectToCrawlerWebSocket }) => {
						connectToCrawlerWebSocket(jobId);
					});
				}, 500);

				console.log('[Service Status]', $serviceStatus);
				goto('/crawler/run', { replaceState: true });
			} else {
				await update();
			}
		};
	};
</script>

<svelte:head>
	<title>Crawler Configuration | TRACE</title>
</svelte:head>

<div class="crawler-config">
	<div class="title-section">
		<div class="title">Crawler Configuration</div>
		<StepIndicator status="config" />
	</div>
	<form method="POST" use:enhance={onSubmitHandler} class="input-container">
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
	.crawler-config {
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
