<script>
	import { Input } from '$lib/components/ui/input/index.js';
	import { Label } from '$lib/components/ui/label/index.js';
	import * as Tooltip from '$lib/components/ui/tooltip/index.js';
	import { Button } from '$lib/components/ui/button/index.js';
	import { Info } from 'lucide-svelte';

	export let field;
	export let value = '';
	export let error = false;
	export let errorText = '';
	export let onInput = () => {};
	export let onBlur = () => {};

	let id, label, type, placeholder, required, toolTip;
	$: {
		id = field?.id;
		label = field?.label;
		type = field?.type ?? 'text';
		placeholder = field?.placeholder ?? '';
		required = field?.required ?? false;
		toolTip = field?.toolTip ?? null;
	}

	let errorId, tooltipId, describedBy;
	$: {
		errorId = error ? `${id}-error` : null;
		tooltipId = toolTip ? `${id}-tooltip` : null;
		describedBy = [errorId, tooltipId].filter(Boolean).join(' ') || undefined;
	}
</script>

<div class="input-field">
	<div class={`flex items-center gap-1 ${!toolTip ? 'mb-[6px]' : 'mt-[-6px]'}`}>
		<Label for={id} class="text-sm font-medium">
			{label}
			{#if required}
				<span class="text-red-500">*</span>
			{/if}
		</Label>

		{#if toolTip}
			<Tooltip.Provider>
				<Tooltip.Root>
					<Tooltip.Trigger asChild>
						<Button
							variant="ghost"
							size="circlesm"
							type="button"
							aria-label={`More info about ${label}`}
						>
							<Info style="width: 16px; height: 16px;" />
						</Button>
					</Tooltip.Trigger>
					<Tooltip.Content id={tooltipId} side="top" align="start">
						<p class="max-w-xs text-sm">{toolTip}</p>
					</Tooltip.Content>
				</Tooltip.Root>
			</Tooltip.Provider>
		{/if}
	</div>

	<Input
		{id}
		name={id}
		{label}
		{type}
		{placeholder}
		{value}
		oninput={onInput}
		onblur={onBlur}
		{error}
		aria-describedby={describedBy}
	/>

	{#if error}
		<p id={errorId} class="text-error mt-1 text-sm">{errorText}</p>
	{/if}
</div>

<style>
	.input-field {
		display: flex;
		flex-direction: column;
		width: 100%;
		max-width: 24rem;
	}
</style>
