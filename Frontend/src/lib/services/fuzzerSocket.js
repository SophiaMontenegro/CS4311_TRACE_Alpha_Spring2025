import { serviceStatus } from '$lib/stores/projectServiceStore';
import {
	scanProgress,
	stopScanProgress,
	startScanProgress,
	scanPaused
} from '$lib/stores/scanProgressStore';
import { serviceResults } from '$lib/stores/serviceResultsStore.js';
import { get } from 'svelte/store';
import { getApiBaseURL } from '$lib/utils/apiBaseURL';

let socket = null;

/**
 * Establishes a WebSocket connection to the backend fuzzer using the job ID.
 * Automatically retries connection if it fails (up to maxRetries).
 */
export function connectToFuzzerWebSocket(jobId, retry = 0) {
	const maxRetries = 5;

	// Prevent duplicate connections if one is already open
	if (socket && socket.readyState !== WebSocket.CLOSED) {
		console.warn('[WebSocket] Already connected. Skipping duplicate connection.');
		return;
	}

	// apiBaseURL is fetched from a utility function
	const apiBaseURL = getApiBaseURL();
	const wsBaseURL = apiBaseURL.replace('http', 'ws');

	// Open a WebSocket connection to the backend endpoint
	socket = new WebSocket(`${wsBaseURL}/ws/fuzzer/${jobId}`);

	// Triggered when the connection is successfully established
	socket.onopen = () => {
		console.log('[WebSocket] Connected to fuzzer job:', jobId);

		// Checkpoint restore logic on successful (re)connect
		const savedCheckpoint = localStorage.getItem(`checkpoint_${jobId}`);
		if (savedCheckpoint) {
			try {
				const parsed = JSON.parse(savedCheckpoint);
				if (Array.isArray(parsed) && parsed.length > 0) {
					serviceResults.update((r) => ({
						...r,
						fuzzer: parsed
					}));
					console.log('[Restore] Checkpoint loaded for job:', jobId);
				}
			} catch (err) {
				console.error('[Restore] Failed to parse checkpoint data:', err);
			}
		}
	};

	// Triggered whenever a message is received from the backend
	socket.onmessage = (event) => {
		const message = JSON.parse(event.data);
		const { type, data } = message;

		switch (type) {
			// Updates job status in the serviceStatus store
			case 'status': {
				const mappedStatus = data.status;
				const current = get(serviceStatus);

				// Ignore downgrades from completed → idle
				if (current.status === 'completed' && mappedStatus === 'idle') {
					console.warn('[Fuzzer] Ignoring idle status after completion');
					return;
				}

				// handle pause/resume toggling
				switch (mappedStatus) {
					case 'paused':
						scanPaused.set(true);
						break;
					case 'running':
						scanPaused.set(false);
						break;
				}

				serviceStatus.set({
					status: mappedStatus,
					serviceType: 'fuzzer',
					startTime: data.started_at || new Date().toISOString()
				});
				break;
			}

			// Updates the fuzzer result table with a new scanned row
			case 'new_row':
				serviceResults.update((r) => ({
					...r,
					fuzzer: [...r.fuzzer, data.row]
				}));
				break;

			// Updates the progress of the fuzzer job
			case 'progress':
				if (get(serviceStatus).status === 'completed') {
					console.warn('[Fuzzer] Ignoring late progress update');
					return;
				}
				if (!get(scanPaused)) {
					startScanProgress('fuzzer');
					scanProgress.set(Math.min(data.progress, 99));
				}
				break;

			// Marks the scan as completed and finalizes UI
			case 'completed':
				scanProgress.set(100);
				stopScanProgress(true);
				serviceStatus.set({
					status: 'completed',
					serviceType: 'fuzzer',
					startTime: null
				});
				break;

			// Handles errors and resets UI state
			case 'error': {
				console.error('[Fuzzer Error]', data.message);

				if (data.message?.includes('not found')) {
					localStorage.removeItem(`checkpoint_${jobId}`);
					serviceResults.update((r) => ({ ...r, fuzzer: [] }));
				}

				serviceStatus.set({
					status: 'error',
					serviceType: 'fuzzer',
					startTime: null
				});
				break;
			}
		}
	};

	// Handles WebSocket connection errors and retries if needed
	socket.onerror = (e) => {
		console.error('[WebSocket Error]', e);

		// Set UI status to error
		serviceStatus.set({
			status: 'error',
			serviceType: 'fuzzer',
			startTime: null
		});

		if (retry < maxRetries) {
			console.log(`[WebSocket] Retrying connection (${retry + 1}/${maxRetries})...`);
			setTimeout(() => connectToFuzzerWebSocket(jobId, retry + 1), 1000);
		} else {
			// Close the socket and clean up after max retries
			if (socket) {
				socket.close();
				socket = null;
				console.warn('[WebSocket] Max retries reached. Socket forcibly closed.');
			}
		}
	};

	// Cleans up socket reference when connection is closed
	socket.onclose = () => {
		console.log('[WebSocket] Connection closed');
		socket = null;

		// Only set error if the scan wasn't completed or manually stopped
		const currentStatus = get(serviceStatus);
		if (['running', 'paused'].includes(currentStatus.status)) {
			serviceStatus.set({
				status: 'error',
				serviceType: 'fuzzer',
				startTime: null
			});
		}
	};
}

/**
 * Manually closes the WebSocket connection.
 */
export function closeFuzzerWebSocket() {
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
