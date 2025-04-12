<script lang="ts">
	import { cn } from "$lib/utils.js";

	export let size: 'sm' | 'md' | 'lg' = 'md';

	const sizeClasses = {
		sm: 'w-4 h-4 border-2',
		md: 'w-8 h-8 border-4',
		lg: 'w-12 h-12 border-4'
	};
</script>

<div
	role="status"
	class={cn(
		`inline-block animate-spin rounded-full border-solid border-accent border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite] ${sizeClasses[size]}`
	)}
>
	<span class="sr-only">Loading...</span>
</div>

<style>
	.sr-only {
		position: absolute;
		width: 1px;
		height: 1px;
		padding: 0;
		margin: -1px;
		overflow: hidden;
		clip: rect(0, 0, 0, 0);
		white-space: nowrap;
		border: 0;
	}
</style>
