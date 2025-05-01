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
			injectable_params: formData["injectable-params"],
			custom_flags: formData["custom-flags"],
			db_user: formData["db-user"],
			db_pass: formData["db-pass"],
			enum_level: formData["enum-level"] ? Number(formData["enum-level"]) : undefined,
			timeout: formData["timeout"] ? Number(formData["timeout"]) : undefined,
			additional: formData["additional"],
			db_enum: formData["db-enum"] === "on"
		};

		try {
            const apiBaseURL = formData["api-base-url"];
            if (!apiBaseURL) throw new Error('API Base URL is not set!');
            console.log("Sending sql injection config to:", apiBaseURL);
			const response = await fetch("${apiBaseURL}/api/sqlinjection", {
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
				message: "SQL Injection test started successfully!",
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
	}
};