import { writable } from 'svelte/store';

/*
 * Creates a writable store for managing the results of a service (like the crawler).
 * The store is persisted to localStorage so the UI can recover state on refresh.
 */
export const serviceResults = writable({
	crawler: [],
	credGenAI: [],
	bruteForce: [],
	fuzzer: [],
});

