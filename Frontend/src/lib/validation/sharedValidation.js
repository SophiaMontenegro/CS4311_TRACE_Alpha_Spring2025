/**
 * Validates numeric fields
 * @param {string|number} value - The numeric value to validate
 * @returns {Object} - Validation result with error flag and message
 */
export function validateNumeric(value) {
	if (value && (isNaN(value) || Number(value) < 0)) {
		return { error: true, message: 'Must be a non-negative number' };
	}
	return { error: false, message: '' };
}