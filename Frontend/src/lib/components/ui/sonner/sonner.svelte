<script>
	import { Toaster as Sonner } from "svelte-sonner";
	import { mode } from "mode-watcher";

	let { ...restProps } = $props();
</script>

<Sonner
	theme={$mode}
	class="toaster group"
	toastOptions={{
		classes: {
			toast:
				"group toast group-[.toaster]:bg-background group-[.toaster]:text-accent group-[.toaster]:border-border group-[.toaster]:shadow-lg",
			description: "group-[.toast]:text-foreground",
			actionButton: "group-[.toast]:bg-primary group-[.toast]:text-primary-foreground",
			cancelButton: "group-[.toast]:bg-background1 group-[.toast]:text-foreground",
		},
	}}
	{...restProps}
/>
