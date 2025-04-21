/**
 * Validates the headers input field.
 * Ensures each line is in "Key: Value" format.
 * Empty values are considered valid since the field is optional.
 *
 * @param {string} value - The full header string (e.g., multiline textarea).
 * @returns {Object} - { error: boolean, message: string }
 */
export function validateHeaders(value) {
    if (!value?.trim()) {
      return { error: false, message: '' }; // Field is optional
    }
  
    const lines = value.split(/\r?\n/);
  
    const invalidLines = lines.filter((line) => {
      const trimmed = line.trim();
      // Allow empty lines
      if (!trimmed) return false;
  
      // Must contain a colon separating key and value
      const parts = trimmed.split(':');
      return parts.length < 2 || !parts[0].trim() || !parts[1].trim();
    });
  
    if (invalidLines.length > 0) {
      return {
        error: true,
        message: `Header lines must be in "Key: Value" format. Invalid line(s):\n${invalidLines.join('\n')}`
      };
    }
  
    return { error: false, message: '' };
  }
  