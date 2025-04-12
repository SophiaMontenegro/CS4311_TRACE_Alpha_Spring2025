<script>
	import { Skeleton } from '$lib/components/ui/skeleton/index.js';
	export let data = [];
	export let columns = [];

	function truncateMiddle(str, maxLength = 30) {
		if (!str || typeof str !== 'string' || str.length <= maxLength) return str;
		const keep = Math.floor(maxLength / 2) - 1;
		return str.slice(0, keep) + '...' + str.slice(-keep);
	}

	$: paddedRows = data.length >= 8 ? data : [...data, ...Array(8 - data.length).fill(null)];
</script>

<div class="container flex flex-col items-center justify-center">
	<div class="table-body rounded-lg shadow-[0_8px_30px_rgb(0,0,0,0.12)]">
		<table class="w-full border-collapse">
			<thead class="sticky-header">
				<tr class="bg-accent text-foreground">
					{#each columns as column}
						<th class="p-2 text-left">{column.label}</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each paddedRows as row, i}
					<tr class={i % 2 === 0 ? 'bg-background1' : 'bg-background2'}>
						{#each columns as column}
							<td
								class="max-w-[220px] overflow-hidden text-ellipsis whitespace-nowrap border-t p-2"
							>
								{#if row}
									{#if column.isLink}
										<a
											href={row[column.key]}
											target="_blank"
											rel="noopener noreferrer"
											title={row[column.key]}
											class="block text-blue-600 underline"
										>
											{truncateMiddle(row[column.key], 40)}
										</a>
									{:else}
										<span class="block truncate">{row[column.key]}</span>
									{/if}
								{:else}
									<span class="block">&nbsp;</span>
								{/if}
							</td>
						{/each}
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<style>
	.container {
		width: 90%;
		max-width: 100%;
		padding: 4rem;
	}
	.table-body {
		max-height: 400px;
		max-width: 1200px;
		overflow-y: auto;
		width: 100%;
		display: flex;
		justify-content: center;
	}
	table {
		font-size: 14px;
		width: 100%;
		margin: auto;
		border-collapse: collapse;
	}
	.sticky-header {
		position: sticky;
		top: 0;
		background: var(--accent);
		z-index: 10;
	}
	th {
		font-weight: 700;
		text-align: left;
	}
	td {
		font-weight: 400;
	}
	@media (max-width: 768px) {
		.container {
			overflow-x: auto;
		}
	}
	::-webkit-scrollbar {
		display: none;
	}
</style>
