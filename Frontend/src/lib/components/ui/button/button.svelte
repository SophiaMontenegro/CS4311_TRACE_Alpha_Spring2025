<script module>
	import { tv } from "tailwind-variants";

	export const buttonVariants = tv({
		base: "ring-offset-background focus-visible:ring-ring inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
		variants: {
			variant: {
				default: "bg-accent text-foreground hover:bg-accent3",
				defaultSec: "bg-accent2 text-foreground hover:bg-accent3",
				destructive: "bg-error text-background hover:bg-error-hover",
				outline: "border-input bg-background hover:bg-accent hover:text-accent-foreground border",
				secondary: "bg-background2 text-foreground hover:bg-background3 hover:text-background2-foreground data-[active=true]:bg-accent data-[active=true]:text-background",
				ghost: "text-primary",
				link: "text-primary underline-offset-4 hover:underline",
				circle: "bg-background2 text-background2-foreground hover:bg-background3 hover:text-background2-foreground rounded-full drop-shadow-md data-[active=true]:bg-accent data-[active=true]:text-foreground",
			},
			size: {
				default: "h-10 px-4 py-2 rounded-lg text-md font-medium",
				sm: "h-9 px-3 rounded-lg text-sm font-small",
				lg: "h-11 px-8 rounded-lg text-md font-medium",
				icon: "h-10 w-10",
				circle: "h-10 w-10",
				circlesm: "h-8 w-8",
			},
		},
		defaultVariants: {
			variant: "default",
			size: "default",
		},
	});
</script>

<script>
	import { cn } from "$lib/utils.js";

	let {
		class: className,
		variant,
		size,
		ref = $bindable(null),
		href = undefined,
		type = 'submit',
		children,
		...restProps
	} = $props();
</script>

{#if href}
	<a
		bind:this={ref}
		class={cn(buttonVariants({ variant, size }), className)}
		href={href}
		{...restProps}
	>
		{@render children?.()}
	</a>
{:else}
	<button
		type={type}
		bind:this={ref}
		class={cn(buttonVariants({ variant, size }), className)}
		{...restProps}
	>
		{@render children?.()}
	</button>
{/if}
