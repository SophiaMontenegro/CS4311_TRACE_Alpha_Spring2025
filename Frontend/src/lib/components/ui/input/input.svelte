<script>
	import { cn } from "$lib/utils.js";

	let {
		ref = $bindable(null),
		value = $bindable(),
		type,
		files = $bindable(),
		class: className,
		error = false,
		infoText = null,
		...restProps
	} = $props();
</script>

{#if type === "file"}
	<div class="w-full">
		<input
			bind:this={ref}
			class={cn(
				"border-input border-background3 bg-background ring-offset-background placeholder:text-foreground focus-visible:ring-accent3-hover flex h-10 w-full rounded-md border-1.5 px-3 py-2 text-base file:border-0 file:bg-transparent file:text-md file:font-medium focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50 md:text-md",
				error && "border-error focus-visible:ring-error-outline",
				className
			)}
			type="file"
			bind:files
			bind:value
			aria-invalid={error}
			aria-describedby={restProps['aria-describedby']}
			{...restProps}
		/>
	</div>
{:else}
	<div class="w-full">
		<input
			bind:this={ref}
			class={cn(
				"no-spinner border-input border-background3 bg-background ring-offset-background placeholder:text-background3 focus-visible:ring-accent3-hover flex h-10 w-full rounded-md border-1.5 px-3 py-2 text-base focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50 md:text-md",
				error && "border-error focus-visible:ring-error-outline",
				className
			)}
			{type}
			bind:value
			aria-invalid={error}
			aria-describedby={restProps['aria-describedby']}
			{...restProps}
		/>
	</div>
{/if}

<style>
	.no-spinner {
			appearance: textfield;
			-moz-appearance: textfield;
	}
	.no-spinner::-webkit-inner-spin-button,
	.no-spinner::-webkit-outer-spin-button {
			-webkit-appearance: none;
			margin: 0;
	}
</style>