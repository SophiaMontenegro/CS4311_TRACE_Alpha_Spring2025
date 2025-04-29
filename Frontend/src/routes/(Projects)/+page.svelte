<script>
	import { goto } from '$app/navigation';
	import { Button } from '$lib/components/ui/button';
	import { mode, toggleMode  } from 'mode-watcher';
</script>

<div class="relative h-screen bg-background text-foreground">
	<div
		class="absolute inset-0 bg-no-repeat bg-top bg-contain pointer-events-none"
		style="background-image: url({$mode === 'dark' ? '/icons/patternDark.svg' : '/icons/patternLight.svg'});"
	></div>

	<div class="relative z-10 flex h-screen flex-col px-6 py-6">
		<div class="mb-6 flex items-center justify-between">
			<Button
				variant="ghost"
				size="icon"
				type="button"
				title="Toggle Theme"
				aria-label="Toggle Theme"
				onclick={toggleMode}
			>
				{#if $mode === 'dark'}
					<img src="/icons/traceDarkIcon.svg" alt="Dark Mode Icon" style="width: 2.5rem; height: 2.5rem;" />
				{:else}
					<img src="/icons/traceLightIcon.svg" alt="Light Mode Icon" style="width: 2.5rem; height: 2.5rem;" />
				{/if}
			</Button>
		</div>

		<div class="flex flex-grow flex-col items-center justify-center text-center">
			<div class="mb-4 text-5xl font-bold leading-tight">
				Elevate Your Security<br />Strategy with TRACE
			</div>
			<div class="text-foreground mb-8 max-w-xl text-md">
				A Cybersecurity Platform to Protect Your Digital Assets. Detect Vulnerabilities, Strengthen
				Defense, and Secure Your Network Seamlessly. Gain Real-Time Insights and Proactive Protection.
			</div>
			<Button
				default="secondary"
				size="lg"
				onclick={() => goto('/login')}
				aria-label="Start a session"
				title="Click to start a session"
			>
				START
			</Button>
		</div>
	</div>
</div>
