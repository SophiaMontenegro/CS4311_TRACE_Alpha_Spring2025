/**
 * Validates a string of parameters separated by commas.
 * It ensures that the input is not empty, trims whitespace, and checks for valid parameters.
 * @param {string} value - The input string containing parameters separated by commas.
 * @returns {Object} - Validation result with an error flag and a message.
 *                     If validation fails, `error` is true and `message` contains the error description.
 *                     If validation succeeds, `error` is false and `message` is an empty string.
 */
export function validateParameters(value) {
	if (!value?.trim()) {
		return { error: true, message: 'At least one parameter is required.' };
	}

	const params = value
		.split(',')
		.map((p) => p.trim())
		.filter(Boolean);
	if (params.length === 0) {
		return { error: true, message: 'Please provide valid parameters.' };
	}

	return { error: false, message: '' };
}

/**
 * Validates the body template field used for POST requests.
 * Ensures that the template includes the "payload" keyword as a placeholder.
 * Returns an error if "payload" is not found. Empty values are allowed.
 *
 * @param {string} value - The body template string to validate.
 * @returns {Object} - Validation result with error flag and message.
 */
export function validateBodyTemplate(value) {
	if (!value?.trim()) return { error: false, message: '' }; // optional

	// Basic heuristic: should contain payload placeholders
	if (!value.includes('payload')) {
		return {
			error: true,
			message: 'Template must include "payload" placeholders.'
		};
	}

	return { error: false, message: '' };
}
