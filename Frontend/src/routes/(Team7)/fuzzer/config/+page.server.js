import { fail } from '@sveltejs/kit';
import { validateField } from '$lib/validation/fieldValidatorFactory.js';

/** @type {import('./$types').Actions} */
export const actions = {
	default: async ({ request }) => {
		const rawFormData = await request.formData();

		const wordlist = rawFormData.get('wordlist'); // File
		const formData = Object.fromEntries(rawFormData.entries());
		delete formData.wordlist;

		const fieldErrors = {};

		// Validate all inputs
		for (const [id, value] of Object.entries(formData)) {
			const result = validateField(id, value);
			if (result.error) {
				fieldErrors[id] = { error: true, message: result.message };
			}
		}

		// Validate the uploaded wordlist
		const fileValidation = validateField('wordlist', wordlist);
		if (fileValidation.error) {
			fieldErrors.wordlist = {
				error: true,
				message: fileValidation.message
			};
		}

		// Check required fields
		const requiredFields = ['target-url', 'parameters', 'http-method'];
		for (const field of requiredFields) {
			if (!formData[field]) {
				fieldErrors[field] = {
					error: true,
					message: `${field.replace('-', ' ')} is required.`
				};
			}
		}

		if (Object.keys(fieldErrors).length > 0) {
			return fail(400, {
				error: true,
				fieldErrors,
				values: formData
			});
		}

		// Convert wordlist file to payload array
		let payloads = [];
		if (wordlist) {
			const fileText = await wordlist.text();
			payloads = fileText
				.split('\n')
				.map((line) => line.trim())
				.filter((line) => line.length > 0);
		}

		let parsedHeaders = {
			"Content-Type": "application/json",
			"User-Agent": "TRACE-Fuzzer/1.0"
		};

		if (formData['headers']) {
			try {
				const entries = formData['headers']
					.split(',')
					.map((pair) => pair.split(':').map((s) => s.trim()))
					.filter(([key, val]) => key && val);
				parsedHeaders = Object.fromEntries(entries);
			} catch {
				return fail(400, {
					error: true,
					message: 'Invalid headers format. Use "key: value, key2: value2"',
					values: formData
				});
			}
		}

		// Construct final config object
		const configForBackend = {
			"target-url": formData['target-url'],
			"http-method": formData['http-method'],
			"headers": parsedHeaders,
			"parameters": formData['parameters'].split(',').map((p) => p.trim()),
			"payloads": payloads,
			"show-status": [],
			"hide-status": [],
			"proxy": formData['proxy'] || ""
		};

		try {
			const response = await fetch('http://127.0.0.1:8000/api/fuzzer', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Accept: 'application/json'
				},
				body: JSON.stringify(configForBackend)
			});

			const json = await response.json();

			if (!response.ok) {
				return fail(response.status, {
					error: true,
					message: `Backend error: ${json?.detail || response.statusText}`,
					values: formData
				});
			}

			return {
				success: true,
				message: 'Fuzzer scan started successfully!',
				values: formData,
				job_id: json?.job_id
			};
		} catch (error) {
			console.error('Uncaught server error:', error);
			return fail(500, {
				error: true,
				message: 'Internal server error',
				values: formData
			});
		}
	}
};
