/**
 * Validates the attempt limit to ensure it is a non-negative integer or -1.
 * @param {string} value - The value to validate as an attempt limit.
 * @returns {Object} - Validation result containing an error flag and a message.
 */
export function validateAttemptLimit(value) {
	const num = parseInt(value);
	if (isNaN(num) || !Number.isInteger(num)) {
		return { error: true, message: 'Attempt limit must be an integer.' };
	}
	if (num < -1) {
		return { error: true, message: 'Only -1 is allowed for unlimited attempts.' };
	}
	return { error: false, message: '' };
}

/**
 * Validates a string of status codes.
 * @param {string} value - A comma-separated string of status codes to validate.
 * @returns {Object} - Validation result with an error flag and a message.
 * @property {boolean} error - Indicates whether the validation failed.
 * @property {string} message - Provides details about the validation result.
 */
export function validateStatusCodes(value) {
	if (!value) return { error: false, message: '' };
	const codes = value.split(',').map((code) => code.trim());
	const isValid = codes.every((code) => /^\d{3}$/.test(code));
	return isValid
		? { error: false, message: '' }
		: { error: true, message: 'Status codes must be three-digit numbers separated by commas.' };
}

/**
 * Validates a content length filter string.
 * @param {string} value - The filter string to validate. Example format: ">100, <500".
 * @returns {Object} - Validation result containing:
 *   - {boolean} error: Indicates if the validation failed.
 *   - {string} message: Error message if validation fails, otherwise an empty string.
 */
export function validateContentLengthFilter(value) {
	if (!value) return { error: false, message: '' };
	const regex = /^([<>]=?\d+\s*,?\s*)+$/;
	return regex.test(value)
		? { error: false, message: '' }
		: { error: true, message: 'Use format like >100, <500 with commas separating conditions.' };
}

/**
 * Validates that the top-level directory path starts with a slash (/).
 * @param {string} value - The directory path to validate.
 * @returns {Object} - Validation result containing an error flag and a message.
 */
export function validateTopLevelDirectory(value) {
	if (!value) return { error: false, message: '' }; // Allow empty (default root)
	if (typeof value !== 'string' || !value.startsWith('/')) {
		return { error: true, message: 'Directory path must start with "/"' };
	}
	return { error: false, message: '' };
}
