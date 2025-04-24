<script>
	import { onMount } from 'svelte';
	import * as d3 from 'd3';

	let treeData = null;
	let selectedNode = null;
	let svgElement;
	let zoomBehavior;
	let currentZoom = 1;

	async function loadTreeData() {
		const visibleRes = await fetch('/webtree/dummy_tree.json');
		const hiddenRes = await fetch('/webtree/hidden_tree.json');

		const visibleData = await visibleRes.json();
		const hiddenData = await hiddenRes.json();
		
		const combined = [...visibleData, ...hiddenData];
		if (JSON.stringify(combined) !== JSON.stringify(treeData)) {
			treeData = combined;
			renderTreeGraph();
		}
	}

	onMount(() => {
		loadTreeData();
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

	function renderTreeGraph() {
		const width = window.innerWidth;
		const height = window.innerHeight * 0.9;

		d3.select('#tree').select('svg').remove();

		svgElement = d3.select('#tree').append('svg').attr('width', width).attr('height', height);

		const zoomGroup = svgElement.append('g');

		zoomBehavior = d3.zoom().on('zoom', (event) => {
			zoomGroup.attr('transform', event.transform);
		});

		svgElement.call(zoomBehavior).call(zoomBehavior.transform, d3.zoomIdentity.scale(currentZoom));

		const svg = zoomGroup.append('g');

		svg
			.append('rect')
			.attr('width', width)
			.attr('height', height)
			.attr('fill', 'transparent')
			.lower() // This keeps it behind everything
			.on('click', () => {
				selectedNode = null;
			});

		treeData.forEach((treeRoot, index) => {
			const root = d3.hierarchy(treeRoot);
			const treeLayout = d3
				.tree()
				.size([width, height])
				.separation((a, b) => (a.parent === b.parent ? 2 : 1));

			treeLayout(root);

			const rootNode = root; // root node of this tree

			if (treeRoot.path === '/') {
				const centerX = width / 2 - root.x;
				const centerY = height / 2 - root.y;

				zoomGroup.attr('transform', `translate(${centerX}, ${centerY})`);
				svgElement
					.transition()
					.duration(300)
					.call(
						zoomBehavior.transform,
						d3.zoomIdentity.translate(centerX, centerY).scale(currentZoom)
					);
			}

			// Apply vertical offset based on index to stack roots vertically
			const isHiddenGroup = treeRoot.hidden === true;
			root.descendants().forEach((d) => {
				d.x = (d.x - 50) * 3;
				d.y = d.depth * 180 + (isHiddenGroup ? 800 : 0); // Push hidden nodes down
			});

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
				.attr('fill', '#f3f4f6')
				.attr('stroke', '#d1d5db')
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
				.attr('fill', '#1f2937')
				.text((d) => d.data.node_id);

			nodeGroup
				.append('text')
				.attr('x', 0)
				.attr('y', 15)
				.attr('text-anchor', 'middle')
				.attr('font-size', '14px')
				.attr('font-weight', 'bold')
				.attr('fill', '#111827')
				.text((d) => d.data.name);
		});
	}

	let newSeverity = '';

	function updateSeverity() {
		if (!selectedNode || !newSeverity) return;

		fetch('http://localhost:8000/api/tree/update', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				ip: selectedNode.node_id,
				path: selectedNode.name,
				severity: newSeverity
			})
		})
			.then((res) => {
				if (res.ok) {
					alert('Severity updated!');
					selectedNode = null;
					newSeverity = '';
					loadTreeData(); // Refresh UI
				} else {
					alert('Server error: ' + res.status);
				}
			})
			.catch((err) => {
				console.error('Fetch error:', err);
				alert('Network error: ' + err.message);
			});
	}
</script>

<!-- Tree Container -->
<div id="tree"></div>

<!-- Zoom Controls -->
<div class="zoom-controls">
	<button on:click={zoomOut}>➖</button>
	<button on:click={zoomIn}>➕</button>
</div>

<!-- Node Popup -->
{#if selectedNode}
	<div class="popup">
		<div class="popup-content">
			<h3>Node Details</h3>
			<p><strong>ID:</strong> {selectedNode.node_id}</p>
			<p><strong>Name:</strong> {selectedNode.name}</p>
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
		top: 20%;
		left: 50%;
		transform: translateX(-50%);
		background: rgba(0, 0, 0, 0.3);
		width: 100vw;
		height: 100vh;
		z-index: 1000;
	}

	.popup-content {
		position: absolute;
		top: 30%;
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
</style>
