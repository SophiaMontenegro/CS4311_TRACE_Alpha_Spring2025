/**
 * Validates a length value for username or password fields.
 * It ensures the value is a number, is greater than zero, and is an integer.
 * @param {string|number} value - The length value to validate.
 * @returns {Object} - Validation result with error flag and message.
 */
export function validateLength(value) {
	if (!value) {
		return { error: false, message: '' };
	}
	if (isNaN(Number(value))) {
		return { error: true, message: 'Length must be a number.' };
	}
	if (Number(value) <= 0) {
		return { error: true, message: 'Length must be greater than zero.' };
	}
	if (!Number.isInteger(Number(value))) {
		return { error: true, message: 'Length must be an integer.' };
	}
	return { error: false, message: '' };
}