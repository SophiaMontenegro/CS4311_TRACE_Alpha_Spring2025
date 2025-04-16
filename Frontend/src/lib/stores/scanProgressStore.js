import { writable, get } from 'svelte/store';
import { serviceStatus } from './projectServiceStore';

export const scanProgress = writable(0);
export const scanPaused = writable(false);
export const currentService = writable(null);

let intervalId = null;
let alreadyStopped = false;

export function startScanProgress(service) {
	if (intervalId !== null || get(serviceStatus).status === 'running') return;

	alreadyStopped = false;
	currentService.set(service);
	scanProgress.set(0);
	scanPaused.set(false);

	serviceStatus.set({
		status: 'running',
		serviceType: service,
		startTime: new Date().toISOString()
	});

	console.log('[Scan] Progress started for:', service);
}

export function stopScanProgress(markComplete = false) {
	if (alreadyStopped) return;
	alreadyStopped = true;

	if (intervalId) {
		clearInterval(intervalId);
		intervalId = null;
	}

	const service = get(currentService);

	if (markComplete && service) {
		serviceStatus.set({
			status: 'completed',
			serviceType: service,
			startTime: null
		});
	} else {
		serviceStatus.set({
			status: 'idle',
			serviceType: null,
			startTime: null
		});
		scanProgress.set(0);
	}

	scanPaused.set(false);
	currentService.set(null);
	console.log('[Scan] Progress stopped');
}

export async function pauseScan(service) {
	const jobId = localStorage.getItem(`current${capitalize(service)}JobId`);
	if (!jobId || get(serviceStatus).status !== 'running') return false;

	try {
		const res = await fetch(`http://localhost:8000/api/${service}/${jobId}/pause`, {
			method: 'POST'
		});
		if (!res.ok) throw new Error('Pause failed');

		scanPaused.set(true);
		serviceStatus.update((s) => ({ ...s, status: 'paused' }));
		console.log(`[Scan] ${service} paused`);
		return true;
	} catch (err) {
		console.error(`Failed to pause ${service}:`, err);
		return false;
	}
}

export async function resumeScan(service) {
	const jobId = localStorage.getItem(`current${capitalize(service)}JobId`);
	if (!jobId || get(serviceStatus).status !== 'paused') return false;

	try {
		const res = await fetch(`http://localhost:8000/api/${service}/${jobId}/resume`, {
			method: 'POST'
		});
		if (!res.ok) throw new Error('Resume failed');

		scanPaused.set(false);
		serviceStatus.update((s) => ({ ...s, status: 'running' }));
		console.log(`[Scan] ${service} resumed`);
		return true;
	} catch (err) {
		console.error(`Failed to resume ${service}:`, err);
		return false;
	}
}

// Utility
function capitalize(str) {
	return str.charAt(0).toUpperCase() + str.slice(1);
}
