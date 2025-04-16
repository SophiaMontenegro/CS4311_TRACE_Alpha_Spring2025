import { serviceStatus } from '$lib/stores/projectServiceStore';
import {
	scanProgress,
	stopScanProgress,
	startScanProgress,
	scanPaused
} from '$lib/stores/scanProgressStore';
import { serviceResults } from '$lib/stores/serviceResultsStore.js';
import { get } from 'svelte/store';

let socket = null;

/**
 * Establishes a WebSocket connection to the backend credGenAI using the job ID.
 * Automatically retries connection if it fails (up to maxRetries).
 */
export function connectToCredGenAIWebSocket(jobId, retry = 0) {
	const maxRetries = 5;

	if (!jobId) {
		console.warn('[WebSocket] No job ID provided. Skipping connection.');
		return;
	}

	// Avoid duplicate connections
	if (socket && socket.readyState !== WebSocket.CLOSED) {
		console.warn('[WebSocket] Already connected. Skipping duplicate connection.');
		return;
	}

	socket = new WebSocket(`ws://localhost:8000/ws/ml/${jobId}`);

	socket.onopen = () => {
		console.log('[WebSocket] Connected to credGenAI job:', jobId);
	};

	socket.onmessage = (event) => {
		const message = JSON.parse(event.data);
		const { type, data } = message;

		switch (type) {
			case 'status': {
				let mappedStatus = data.status;

				if (mappedStatus === 'initializing') {
					mappedStatus = 'running';
				}

				serviceStatus.set({
					status: mappedStatus,
					serviceType: 'credGenAI',
					startTime: data.started_at || new Date().toISOString()
				});
				break;
			}

			case 'progress':
				if (!get(scanPaused)) {
					startScanProgress('credGenAI');
					scanProgress.set(Math.min(data.progress, 99));
				}
				break;

			case 'completed': {
				scanProgress.set(100);
				stopScanProgress(true);
				serviceStatus.set({
					status: 'completed',
					serviceType: 'credGenAI',
					startTime: null
				});

				const jobId = localStorage.getItem('currentCredGenAIJobId');
				if (jobId) {
					console.log('[WebSocket] Fetching final results for job:', jobId);
					fetch(`http://localhost:8000/api/ml/${jobId}/results`)
						.then((res) => res.json())
						.then((json) => {
							const parsed = Array.isArray(json) ? json : (json.results ?? []);
							serviceResults.update((r) => ({ ...r, credGenAI: parsed }));
							console.log('[WebSocket] Results set into store:', parsed);
						})
						.catch((err) => console.error('Failed to fetch results after completed:', err));
				}
				break;
			}

			case 'error':
				console.error('[CredGenAI Error]', data.message);
				localStorage.removeItem('currentCredGenAIJobId');
				serviceStatus.set({
					status: 'idle',
					serviceType: 'credGenAI',
					startTime: null
				});
				break;

			case 'log':
				console.log(`[CredGenAI Log] ${data.message}`);
				break;
		}
	};

	socket.onerror = (e) => {
		console.error('[WebSocket Error]', e);
		if (retry < maxRetries) {
			console.log(`[WebSocket] Retrying connection (${retry + 1}/${maxRetries})...`);
			setTimeout(() => connectToCredGenAIWebSocket(jobId, retry + 1), 1000);
		}
	};

	socket.onclose = () => {
		console.log('[WebSocket] Connection closed');
		socket = null;
	};
}

/**
 * Manually closes the WebSocket connection.
 */
export function closeCredGenAIWebSocket() {
	const status = get(serviceStatus).status;

	if (status === 'paused' || status === 'running') {
		console.log('[WebSocket] Not closing — scan still active or paused.');
		return;
	}

	if (socket) {
		socket.close();
		socket = null;
		console.log('[WebSocket] Closed manually.');
	}
}
