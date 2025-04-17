import { fail } from '@sveltejs/kit';
import { validateField } from '$lib/validation/fieldValidatorFactory.js';

/** @type {import('./$types').Actions} */
export const actions = {
	default: async ({ request }) => {
		const rawFormData = await request.formData();

		const wordlistFile = rawFormData.get('wordlist');
		const formData = Object.fromEntries(rawFormData.entries());
		delete formData.wordlist;

		console.log('📥 Received wordlist:', wordlistFile?.name);
		console.log('📦 File size:', wordlistFile?.size);
		console.log('🧾 Form fields:', formData);

		const fieldErrors = {};

		// Validate file
		const fileValidation = validateField('wordlist', wordlistFile);
		if (fileValidation.error || !(wordlistFile instanceof File) || wordlistFile.size === 0) {
			fieldErrors.wordlist = {
				error: true,
				message: fileValidation.message || 'Please upload a valid wordlist file.'
			};
		}

		// Validate text/number fields
		for (const [id, value] of Object.entries(formData)) {
			const result = validateField(id, value);
			if (result.error) {
				fieldErrors[id] = {
					error: true,
					message: result.message
				};
			}
		}

		if (Object.keys(fieldErrors).length > 0) {
			console.warn('Validation errors in credgenAI:', fieldErrors);
			return fail(400, {
				error: true,
				fieldErrors,
				values: formData
			});
		}

		const wordlistText = await wordlistFile.text();

		const jsonPayload = {
			target_urls: ['https://crawler-test.com/'],
			credential_count: formData['credential-count'] ? Number(formData['credential-count']) : 10,
			wordlist: wordlistText,
			min_username_length: formData['username-length'] ? Number(formData['username-length']) : undefined,
			min_password_length: formData['password-length'] ? Number(formData['password-length']) : undefined,
			username_caps: formData['username-caps'] === 'on' ? true : undefined,
			username_numbers: formData['username-numbers'] === 'on' ? true : undefined,
			username_symbols: formData['username-symbols'] === 'on' ? true : undefined,
			password_caps: formData['password-caps'] === 'on' ? true : undefined,
			password_numbers: formData['password-numbers'] === 'on' ? true : undefined,
			password_symbols: formData['password-symbols'] === 'on' ? true : undefined
		};

		try {
			const response = await fetch('http://127.0.0.1:8000/api/ml', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Accept: 'application/json'
				},
				body: JSON.stringify(jsonPayload)
			});

			let json;
			try {
				json = await response.json();
				console.log("Backend response:", json);
			} catch (e) {
				console.warn("Could not parse JSON:", e.message);
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
				message: 'Credential Generator started successfully!',
				values: formData,
				job_id: json?.job_id
			};
		} catch (err) {
			console.error('Uncaught server error:', err);
			return fail(500, {
				error: true,
				message: 'Internal server error',
				values: formData
			});
		}
	}
};
