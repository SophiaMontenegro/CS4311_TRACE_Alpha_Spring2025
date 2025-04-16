/**
 * Validates excluded URLs
 * @param {string} value - Comma-separated list of URLs to validate
 * @returns {Object} - Validation result with error flag and message
 */
export function validateExcludedUrls(value) {
	if (!value) {
		return { error: false, message: '' };
	}

	// Normalize the value by ensuring URLs are comma-separated
	const normalizedValue = value.replace(/(https?:\/\/[^\s,]+)(?=https?:\/\/)/g, '$1,');

	const urls = normalizedValue.split(',').map((u) => u.trim());
	const invalids = urls.filter((url) => !/^https?:\/\/[^\s]+$/.test(url));

	if (invalids.length > 0) {
		return {
			error: true,
			message: 'Each value must be a valid URL starting with http(s)://'
		};
	}

	return { error: false, message: '' };
}

/**
 * Validates a date string
 * @param {string} value - The date string to validate
 * @returns {Object} - Validation result with error flag and message
 */
export function validateDate(value) {
	if (!value) {
		return { error: false, message: '' };
	}

	if (isNaN(Date.parse(value))) {
		return { error: true, message: 'Invalid date format.' };
	}

	return { error: false, message: '' };
}

/**
 * Validates a time string in HH:MM format
 * @param {string} value - The time string to validate
 * @returns {Object} - Validation result with error flag and message
 */
export function validateTime(value) {
	if (!value) {
		return { error: false, message: '' };
	}

	if (!/^\d{2}:\d{2}$/.test(value)) {
		return { error: true, message: 'Time must be in HH:MM format.' };
	}

	return { error: false, message: '' };
}

/**
 * Validates user agent string (no rules yet)
 * @returns {Object} - Validation result with error flag and message
 */
export function validateUserAgent() {
	return { error: false, message: '' };
}

/**
 * Validates the headers input field.
 * Ensures the string follows a basic "key: value" format.
 * Empty values are considered valid since the field is optional.
 *
 * @param {string} value - The header string to validate.
 * @returns {Object} - Validation result with error flag and message.
 */
export function validateHeaders(value) {
	if (!value?.trim()) return { error: false, message: '' }; // optional

	// Basic check for key-value format
	if (!/^[^:]+:\s?.+/.test(value)) {
		return {
			error: true,
			message: 'Header must be in key: value format.'
		};
	}

	return { error: false, message: '' };
}

/**
 * Validates the proxy input field.
 * Ensures the string is a properly formatted HTTP or HTTPS URL.
 * Empty values are allowed since this field is optional.
 *
 * @param {string} value - The proxy URL to validate.
 * @returns {Object} - Validation result with error flag and message.
 */
export function validateProxy(value) {
	if (!value?.trim()) return { error: false, message: '' }; // optional

	if (!/^https?:\/\/[^\s]+$/.test(value)) {
		return { error: true, message: 'Proxy must be a valid http/https URL.' };
	}

	return { error: false, message: '' };
}