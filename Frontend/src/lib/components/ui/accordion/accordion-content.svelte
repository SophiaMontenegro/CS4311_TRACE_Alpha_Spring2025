<script>
	import { Accordion as AccordionPrimitive } from "bits-ui";
	import { cn } from "$lib/utils.js";

	let { ref = $bindable(null), class: className, children, ...restProps } = $props();
</script>

<AccordionPrimitive.Content
	bind:ref
	class={cn(
		"data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down overflow-hidden text-sm transition-all",
		className
	)}
	{...restProps}
>
<div class="pt-2 flex justify-center w-full">
	<div class="w-full flex flex-col gap-4 items-center m-2">
		{@render children?.()}
	</div>
</div>
</AccordionPrimitive.Content>
