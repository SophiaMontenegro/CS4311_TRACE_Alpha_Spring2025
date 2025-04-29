<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';
	import { mode } from 'mode-watcher';

	let treeData = null;
	let selectedNode = null;
	let svgElement;
	let zoomBehavior;
	let currentZoom = 1;

	let showToast = false;
	let toastMessage = '';
	let toastType = 'success';
	let toasts = [];

	let lastFocusPath = '/'; // or null if you prefer no default

	let showExportPopup = false;

	let searchQuery = '';

	function showToastMessage(message, type = 'success') {
		const id = Date.now() + Math.random(); // unique id
		toasts = [...toasts, { id, message, type }];

		setTimeout(() => {
			toasts = toasts.filter((t) => t.id !== id);
		}, 3000);
	}

	async function loadTreeData(focusPath = null) {
		const visibleRes = await fetch(`/webtree/dummy_tree.json?ts=${Date.now()}`);
		const hiddenRes = await fetch(`/webtree/hidden_tree.json?ts=${Date.now()}`);

		const visibleData = await visibleRes.json();
		const hiddenData = await hiddenRes.json();

		const combined = [...visibleData, ...hiddenData];
		if (JSON.stringify(combined) !== JSON.stringify(treeData) || focusPath) {
			treeData = combined;
			lastFocusPath = focusPath || lastFocusPath;
			renderTreeGraph(lastFocusPath);
		}
	}

	onMount(() => {
		loadTreeData('/');
		const interval = setInterval(loadTreeData, 2000); // adjust timing as needed
		return () => clearInterval(interval); // cleanup on unmount
	});

	function getSeverityColor(severity) {
		return severity === 'high' ? '#dc2626' : severity === 'medium' ? '#f59e0b' : '#16a34a';
	}

	function zoomIn() {
		currentZoom = Math.min(3, currentZoom + 0.5);
		svgElement.transition().duration(200).call(zoomBehavior.scaleTo, currentZoom);
	}

	function zoomOut() {
		currentZoom = Math.max(0.3, currentZoom - 0.5);
		svgElement.transition().duration(200).call(zoomBehavior.scaleTo, currentZoom);
	}

	function renderTreeGraph(focusPath = null) {
		const width = window.innerWidth;
		const height = window.innerHeight * 0.9;

		d3.select('#tree').select('svg').remove();

		svgElement = d3.select('#tree').append('svg').attr('width', width).attr('height', height);
		const zoomGroup = svgElement.append('g');
		const svg = zoomGroup.append('g');

		zoomBehavior = d3.zoom().on('zoom', (event) => {
			zoomGroup.attr('transform', event.transform);
		});

		svgElement.call(zoomBehavior).call(zoomBehavior.transform, d3.zoomIdentity.scale(currentZoom));

		svg
			.append('rect')
			.attr('width', width)
			.attr('height', height)
			.attr('fill', 'transparent')
			.lower()
			.on('click', () => {
				selectedNode = null;
			});

		let allDescendants = [];

		treeData.forEach((treeRoot, index) => {
			const root = d3.hierarchy(treeRoot);
			const treeLayout = d3
				.tree()
				.size([width, height])
				.separation((a, b) => (a.parent === b.parent ? 2 : 1));
			treeLayout(root);

			const isHiddenGroup = treeRoot.hidden === true;

			root.descendants().forEach((d) => {
				d.x = (d.x - 50) * 3;
				d.y = d.depth * 180 + (isHiddenGroup ? 800 : 0); // Push hidden nodes down
			});

			allDescendants = allDescendants.concat(root.descendants());

			const group = svg.append('g').attr('class', `root-group-${index}`);

			group
				.selectAll(`line.root-${index}`)
				.data(root.links())
				.enter()
				.append('line')
				.attr('x1', (d) => d.source.x)
				.attr('y1', (d) => d.source.y)
				.attr('x2', (d) => d.target.x)
				.attr('y2', (d) => d.target.y)
				.attr('stroke', '#38bdf8')
				.attr('stroke-width', 2);

			const nodeGroup = group
				.selectAll(`g.node.root-${index}`)
				.data(root.descendants())
				.enter()
				.append('g')
				.attr('class', 'node')
				.attr('transform', (d) => `translate(${d.x},${d.y})`)
				.on('click', (event, d) => {
					selectedNode = d.data;
				});

			nodeGroup
				.append('rect')
				.attr('width', 160)
				.attr('height', 60)
				.attr('x', -80)
				.attr('y', -30)
				.attr('rx', 8)
				.attr('ry', 8)
				.attr('fill', $mode === 'dark' ? '#1f2937' : '#f3f4f6')
				.attr('stroke', $mode === 'dark' ? '#9ca3af' : '#d1d5db')
				.attr('stroke-width', 2)
				.style('stroke-dasharray', (d) => (treeRoot.node_id === 'hidden' ? '4,2' : null));

			nodeGroup
				.append('rect')
				.attr('x', -75)
				.attr('y', -25)
				.attr('width', 150)
				.attr('height', 4)
				.attr('rx', 4)
				.attr('ry', 4)
				.attr('fill', (d) => getSeverityColor(d.data.severity));

			nodeGroup
				.append('text')
				.attr('x', 0)
				.attr('y', -5)
				.attr('text-anchor', 'middle')
				.attr('font-size', '12px')
				.attr('fill', $mode === 'dark' ? '#f3f4f6' : '#1f2937')
				.text((d) => d.data.node_id);

			nodeGroup
				.append('text')
				.attr('x', 0)
				.attr('y', 15)
				.attr('text-anchor', 'middle')
				.attr('font-size', '14px')
				.attr('font-weight', 'bold')
				.attr('fill', $mode === 'dark' ? '#f3f4f6' : '#1f2937')
				.text((d) => d.data.name);
		});

		if (focusPath) {
			const focusNode = allDescendants.find((d) => d.data.name === focusPath);
			if (focusNode) {
				const centerX = width / 2 - focusNode.x;
				const centerY = height / 2 - focusNode.y;

				zoomGroup.attr('transform', `translate(${centerX}, ${centerY})`);
				svgElement
					.transition()
					.duration(300)
					.call(
						zoomBehavior.transform,
						d3.zoomIdentity.translate(centerX, centerY).scale(currentZoom)
					);

				const perimeter = 2 * (160 + 60); // width + height

				svg
					.selectAll('g.node')
					.filter((d) => d.data.name === focusPath)
					.select('rect')
					.attr('stroke', '#facc15') // bright yellow
					.attr('stroke-width', 3)
					.attr('stroke-dasharray', perimeter)
					.attr('stroke-dashoffset', perimeter)
					.transition()
					.duration(600) // total draw time
					.ease(d3.easeLinear)
					.attr('stroke-dashoffset', 0)
					.transition()
					.delay(900)
					.duration(500)
					.attr('stroke', $mode === 'dark' ? '#9ca3af' : '#d1d5db')
					.attr('stroke-width', 2)
					.attr('stroke-dasharray', null)
					.attr('stroke-dashoffset', null);
			}
		}
	}

	let newSeverity = '';

	function updateSeverity() {
		if (!selectedNode || !newSeverity) return;

		const pathToCenter = selectedNode.name;

		fetch('http://localhost:8000/api/tree/update', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				ip: selectedNode.node_id,
				url: selectedNode.url,
				path: selectedNode.path,
				status_code: selectedNode.status_code,
				hidden: selectedNode.hidden,
				severity: newSeverity,
				operation: 'update'
			})
		})
			.then((res) => {
				if (res.ok) {
					showToastMessage('Severity updated!', 'success');
					selectedNode = null;
					newSeverity = '';
					loadTreeData(pathToCenter);
				}
			})
			.catch((err) => {
				console.error('Fetch error:', err);
				showToastMessage('Network error: ' + err.message, 'error');
			});
	}

	$: if (treeData && $mode) {
		renderTreeGraph(lastFocusPath);
	}

	function flattenTree(data, results = [], parentPath = '') {
		data.forEach((node) => {
			results.push({
				ip: node.node_id,
				path: node.name,
				url: node.url,
				severity: node.severity,
				hidden: node.hidden,
				parent: parentPath || '/'
			});
			if (node.children && node.children.length > 0) {
				flattenTree(node.children, results, node.name);
			}
		});
		return results;
	}

	function convertToCSV(rows) {
		const header = Object.keys(rows[0]).join(',') + '\n';
		const body = rows
			.map((row) =>
				Object.values(row)
					.map((v) => `"${v}"`)
					.join(',')
			)
			.join('\n');
		return header + body;
	}

	function downloadCSV() {
		if (!treeData) {
			alert('No data loaded');
			return;
		}

		const flattened = flattenTree(treeData);
		const csv = convertToCSV(flattened);
		const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });

		const filename = `webtree-export-${new Date().toISOString().slice(0, 10)}.csv`;
		const link = document.createElement('a');
		link.href = URL.createObjectURL(blob);
		link.setAttribute('download', filename);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	function flattenTreeToXML(data, parentPath = '/') {
		let xml = '';
		data.forEach((node) => {
			const children = node.children || [];
			xml += `<node`;
			xml += ` path="${node.name}"`;
			xml += ` ip="${node.node_id}"`;
			xml += ` url="${node.url}"`;
			xml += ` severity="${node.severity}"`;
			xml += ` hidden="${node.hidden}"`;
			xml += children.length > 0 ? `>\n` : ` />\n`;

			if (children.length > 0) {
				xml += flattenTreeToXML(children, node.name);
				xml += `</node>\n`;
			}
		});
		return xml;
	}

	function downloadXML() {
		if (!treeData) {
			alert('No data loaded');
			return;
		}

		const xmlContent = `<?xml version="1.0" encoding="UTF-8"?>\n<webtree>\n${flattenTreeToXML(treeData)}</webtree>`;
		const blob = new Blob([xmlContent], { type: 'application/xml;charset=utf-8;' });

		const filename = `webtree-export-${new Date().toISOString().slice(0, 10)}.xml`;
		const link = document.createElement('a');
		link.href = URL.createObjectURL(blob);
		link.setAttribute('download', filename);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}

	function focusSearchResult() {
		if (!treeData || !searchQuery) {
			showToastMessage('Please enter a path to search.', 'error');
			return;
		}

		const allNodes = [];
		const collectNodes = (nodes) => {
			nodes.forEach((n) => {
				allNodes.push(n);
				if (n.children) collectNodes(n.children);
			});
		};

		collectNodes(treeData);

		const trimmedQuery = searchQuery.trim();
		const match = allNodes.find((node) => node.name.toLowerCase() === trimmedQuery.toLowerCase());

		if (match) {
			lastFocusPath = match.name;
			renderTreeGraph(match.name);
			showToastMessage(`Focused on: ${match.name}`, 'success');
		} else {
			showToastMessage(`"${trimmedQuery}" not found.`, 'error');
		}
	}
</script>

<!-- Tree Container -->
<div id="tree"></div>

<div class="search-container">
	<input
		type="text"
		placeholder="Search by path..."
		bind:value={searchQuery}
		on:keydown={(e) => e.key === 'Enter' && focusSearchResult()}
	/>
	<button on:click={focusSearchResult}>Go</button>
</div>

<!-- Zoom Controls -->
<div class="zoom-controls">
	<button on:click={zoomOut}>➖</button>
	<button on:click={zoomIn}>➕</button>
</div>

<!-- Node Popup -->
{#if selectedNode}
	<div class="popup">
		<div class="popup-content" class:dark={$mode === 'dark'}>
			<h3>Node Details</h3>
			<p><strong>ID:</strong> {selectedNode.node_id}</p>
			<p><strong>Name:</strong> {selectedNode.name}</p>
			<p><strong>URL:</strong> {selectedNode.url}</p>
			<select bind:value={newSeverity} on:change={() => console.log(newSeverity)}>
				<option value="" disabled selected>Change severity</option>
				<option value="low">Low</option>
				<option value="medium">Medium</option>
				<option value="high">High</option>
			</select>

			<button on:click={updateSeverity} disabled={!newSeverity}>Save</button>
			<button on:click={() => (selectedNode = null)}>Close</button>
		</div>
	</div>
{/if}

<div class="toast-container">
	{#each toasts as toast (toast.id)}
		<div class="toast {toast.type}">{toast.message}</div>
	{/each}
</div>

{#if showExportPopup}
	<div class="popup">
		<div class="popup-content" class:dark={$mode === 'dark'}>
			<h3>Select Export Format</h3>
			<button
				on:click={() => {
					downloadCSV();
					showExportPopup = false;
				}}>Export as CSV</button
			>
			<button
				on:click={() => {
					downloadXML();
					showExportPopup = false;
				}}>Export as XML</button
			>
			<button on:click={() => (showExportPopup = false)}>Cancel</button>
		</div>
	</div>
{/if}

<button on:click={() => (showExportPopup = true)} class="export-button">Export</button>

<style>
	#tree {
		width: 100%;
		height: 100vh;
		display: flex;
		justify-content: center;
		align-items: start;
		overflow: auto;
	}

	.zoom-controls {
		position: fixed;
		bottom: 20px;
		right: 20px;
		display: flex;
		gap: 10px;
	}

	.zoom-controls button {
		font-size: 24px;
		padding: 10px 15px;
		border: none;
		border-radius: 8px;
		background-color: #2b8bbf;
		color: white;
		cursor: pointer;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
	}

	.zoom-controls button:hover {
		background-color: #247ca1;
	}

	.popup {
		position: fixed;
		top: 0%;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(0, 0, 0, 0.3);
		width: 100vw;
		height: 100vh;
		z-index: 1000;
	}

	.popup-content {
		position: absolute;
		top: 40%;
		left: 50%;
		transform: translate(-50%, -30%);
		background: white;
		padding: 24px;
		border-radius: 12px;
		box-shadow: 0px 8px 16px rgba(0, 0, 0, 0.25);
		min-width: 300px;
	}

	.popup-content h3 {
		margin-bottom: 12px;
	}

	.popup-content button {
		margin-top: 16px;
		background-color: #3b82f6;
		color: white;
		border: none;
		padding: 8px 16px;
		border-radius: 6px;
		cursor: pointer;
	}

	.popup-content button:hover {
		background-color: #2563eb;
	}

	.toast-container {
		position: fixed;
		top: 20px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 10px;
		z-index: 9999;
	}

	.toast {
		background: #4ade80;
		color: white;
		padding: 12px 20px;
		border-radius: 8px;
		font-weight: bold;
		box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
	}

	.toast.success {
		background-color: #4ade80;
	}

	.toast.error {
		background-color: #ef4444;
	}

	.popup-content.dark {
		background-color: #1f2937;
		color: #f9fafb;
	}

	.popup-content.dark button {
		background-color: #2563eb;
		color: white;
	}

	.popup-content.dark button:hover {
		background-color: #1d4ed8;
	}

	.popup-content.dark select,
	.popup-content.dark option {
		background-color: #374151;
		color: #f9fafb;
		border: 1px solid #4b5563;
	}

	.export-button {
		position: fixed;
		top: 20px;
		left: 100px;
		background-color: #3b82f6;
		color: white;
		border: none;
		padding: 8px 16px;
		border-radius: 8px;
		cursor: pointer;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
	}

	.export-button:hover {
		background-color: #2563eb;
	}

	.popup-content button {
		margin-top: 10px;
		width: 100%;
	}

	.search-container {
		position: fixed;
		top: 20px;
		right: 20px;
		display: flex;
		gap: 8px;
	}

	.search-container input {
		padding: 8px;
		border-radius: 6px;
		border: 1px solid #ccc;
		min-width: 200px;
	}

	.search-container button {
		background-color: #3b82f6;
		color: white;
		border: none;
		border-radius: 6px;
		padding: 8px 12px;
		cursor: pointer;
	}

	.search-container button:hover {
		background-color: #2563eb;
	}
</style>
