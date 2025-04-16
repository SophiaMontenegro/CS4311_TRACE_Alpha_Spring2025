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

/**
 * Validates the uploaded wordlist file
 * @param {File|null} file - The uploaded file
 * @returns {Object} - Validation result with error flag and message
 */
export function validateWordlistFile(file) {
	if (!file || file.size === 0) {
		return { error: true, message: 'Wordlist file is required.' };
	}

	if (!file.name.endsWith('.txt')) {
		return { error: true, message: 'Only .txt files are supported.' };
	}

	return { error: false, message: '' };
}

/**
 * Validates a target URL
 * @param {string} url - The URL to validate
 * @returns {Object} - Validation result with error flag and message
 */
export function validateTargetUrl(url) {
	if (!url?.trim()) {
		return { error: true, message: 'Target URL is required.' };
	}
	if (!/^https?:\/\/[^\s/$.?#].[^\s]*$/.test(url.trim())) {
		return { error: true, message: 'Please enter a valid URL.' };
	}
	return { error: false, message: '' };
}