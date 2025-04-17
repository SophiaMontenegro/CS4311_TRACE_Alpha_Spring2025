import { writable } from 'svelte/store';

/**
 * Creates a writable store for managing the status of a running service.
 * The store is persisted to localStorage so the UI can recover state on refresh.
 */
function createServiceStatusStore() {
	// Try to load previously saved state from localStorage (if it exists and we're in a browser)
	const stored = typeof localStorage !== 'undefined' ? localStorage.getItem('serviceStatus') : null;

	// Default state if nothing is stored
	const initial = stored
		? JSON.parse(stored)
		: {
				status: 'idle',        // "idle" | "running" | "completed"
				serviceType: null,     // "crawler", "fuzzer", etc.
				startTime: null        // ISO string of when the service started
			};

	// Create a writable Svelte store with the initial value
	const store = writable(initial);

	// Whenever the store changes, update localStorage
	store.subscribe((value) => {
		if (typeof localStorage !== 'undefined') {
			localStorage.setItem('serviceStatus', JSON.stringify(value));
			console.log('[Store] serviceStatus changed:', value);
		}
	});

	return store;
}

// Export the serviceStatus store so it can be used throughout the app
export const serviceStatus = createServiceStatusStore();
