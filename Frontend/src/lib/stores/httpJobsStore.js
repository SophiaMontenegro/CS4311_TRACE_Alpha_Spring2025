// src/lib/stores/httpJobsStore.js
import { writable } from 'svelte/store';

// LocalStorage key
const STORAGE_KEY = 'httpJobs';

// Load existing jobs from localStorage if available
const saved = typeof localStorage !== 'undefined' ? localStorage.getItem(STORAGE_KEY) : null;

// Default if nothing saved
const initial = saved ? JSON.parse(saved) : {};

// Create the writable store
const httpJobs = writable(initial);

// Subscribe and persist on every change
httpJobs.subscribe((value) => {
	if (typeof localStorage !== 'undefined') {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
	}
});

export { httpJobs };


//TO BE USED, STILL NOT KEEPING WHEN REFRESHING 