import { fail } from '@sveltejs/kit';
import { validateField } from '$lib/validation/fieldValidatorFactory.js';

/** @type {import('./$types').Actions} */
export const actions = {
	default: async ({ request }) => {
		const rawFormData = await request.formData();

		const wordlist = rawFormData.get('wordlist');
		const formData = Object.fromEntries(rawFormData.entries());
		delete formData.wordlist;

		console.log('📥 Received wordlist:', wordlist?.name);
		console.log('📦 File size:', wordlist?.size);
		console.log('🧾 Form fields:', formData);

		const fieldErrors = {};

		for (const [id, value] of Object.entries(formData)) {
			const { error, message } = validateField(id, value);
			if (error) {
				fieldErrors[id] = { error: true, message };
			}
		}

		const fileValidation = validateField('wordlist', wordlist);
		if (fileValidation.error) {
			fieldErrors.wordlist = {
				error: true,
				message: fileValidation.message
			};
		}

		const requiredFields = ['target-url', 'attempt-limit'];
		for (const field of requiredFields) {
			if (!formData[field]) {
				fieldErrors[field] = {
					error: true,
					message: `${field.replace(/-/g, ' ')} is required.`
				};
			}
		}

		if (Object.keys(fieldErrors).length > 0) {
			console.warn('Validation errors:', fieldErrors);
			return fail(400, {
				error: true,
				fieldErrors,
				values: formData
			});
		}

		// Convert wordlist file to array of strings
		let wordlistContents = [];
		if (wordlist) {
			const text = await wordlist.text();
			wordlistContents = text
				.split('\n')
				.map((line) => line.trim())
				.filter(Boolean);
		}

		// Convert headers from "Key: Value, ..." string to object
		let parsedHeaders = {};
		if (formData['headers']) {
			try {
				const entries = formData['headers']
					.split(',')
					.map((pair) => pair.split(':').map((s) => s.trim()))
					.filter(([k, v]) => k && v);
				parsedHeaders = Object.fromEntries(entries);
			} catch {
				return fail(400, {
					error: true,
					message: 'Invalid headers format. Use "Key: Value, Key2: Value2"',
					values: formData
				});
			}
		}

		const toIntArray = (val) =>
			val
				.split(',')
				.map((s) => parseInt(s.trim()))
				.filter((n) => !isNaN(n));

		const transformedData = {
			target_url: formData['target-url'],
			wordlist: wordlistContents,
			top_dir: formData['top-level-directory'] || '',
			hide_status: formData['hide-status-codes'] ? toIntArray(formData['hide-status-codes']) : [],
			show_only_status: formData['show-status-codes']
				? toIntArray(formData['show-status-codes'])
				: [],
			length_filter: formData['filter-content-length']
				? parseInt(formData['filter-content-length'], 10)
				: null,
			headers: parsedHeaders,
			attempt_limit: formData['attempt-limit'] ? parseInt(formData['attempt-limit'], 10) : -1
		};

		try {
			const response = await fetch('http://127.0.0.1:8000/api/dbf', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Accept: 'application/json'
				},
				body: JSON.stringify(transformedData)
			});

			let json;
			try {
				json = await response.json();
				console.log('Backend response:', json);
			} catch {
				console.warn('Could not parse JSON');
			}

			if (!response.ok) {
				return fail(response.status, {
					error: true,
					message: `Backend error: ${response.statusText}`,
					values: formData
				});
			}

			return {
				success: true,
				message: 'Brute Force scan started successfully!',
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
