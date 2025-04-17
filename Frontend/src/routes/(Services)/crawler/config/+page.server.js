import { fail } from '@sveltejs/kit';
import { validateField } from '$lib/validation/fieldValidatorFactory.js';

/** @type {import('./$types').Actions} */
export const actions = {
	default: async ({ request }) => {
		const rawFormData = await request.formData();
		const formData = Object.fromEntries(rawFormData.entries());

		console.log("Received form data:", formData);

		const errors = [];
		for (const [id, value] of Object.entries(formData)) {
			const { error, message } = validateField(id, value);
			if (error) {
				errors.push(`${id}: ${message}`);
			}
		}

		// Ensure required fields exist
		if (!formData['target-url']) {
			errors.push("target-url: Target URL is required.");
		}

		if (errors.length > 0) {
			return fail(400, {
				error: true,
				message: errors.join(" "),
				values: formData
			});
		}

		const transformedData = {
			target_url: formData["target-url"],
			depth: formData["depth"] ? Number(formData["depth"]) : undefined,
			max_pages: formData["max-pages"] ? Number(formData["max-pages"]) : undefined,
			limit: formData["max-pages"] ? Number(formData["max-pages"]) : undefined,
			proxy: formData["proxy"] ? Number(formData["proxy"]) : undefined,
			user_agent: formData["user-agent"] ? formData["user-agent"] : undefined,
			excluded_urls: formData["excluded-urls"] ? formData["excluded-urls"] : undefined,
			crawl_date: formData["crawl-date"] ? formData["crawl-date"] : undefined,
			crawl_time: formData["crawl-time"] ? formData["crawl-time"] : undefined,
		};

		try {
			const response = await fetch("http://127.0.0.1:8000/api/crawler", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Accept: "application/json"
				},
				body: JSON.stringify(transformedData)
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
				message: "All good!",
				values: formData,
				job_id: json?.job_id
			};
		} catch (error) {
			console.error("Uncaught server error:", error);
			return fail(500, {
				error: true,
				message: "Internal server error",
				values: formData
			});
		}

		// FOR TESTING ONLY
		// console.log('Skipping actual backend request for testing...');
		// console.log('Payload that would have been sent:', transformedData);
		
		// return {
		// 	success: true,
		// 	message: 'Simulated fuzzer launch successful (no backend call made).',
		// 	values: formData
		// };
	}
};