import * as crawler from './crawlerValidation.js';
import * as fuzzer from './fuzzerValidation.js';
import * as credGen from './credGenValidation.js';
import * as shared from './sharedValidation.js';

export function validateField(id, value) {
	switch (id) {
		case 'target-url': return crawler.validateTargetUrl(value);
		case 'depth':
		case 'max-pages':
		case 'delay': return shared.validateNumeric(value);
		case 'excluded-urls': return crawler.validateExcludedUrls(value);
		case 'crawl-date': return crawler.validateDate(value);
		case 'crawl-time': return crawler.validateTime(value);
		case 'user-agent': return crawler.validateUserAgent();
		case 'wordlist': return fuzzer.validateWordlistFile(value);
		case 'proxy': return crawler.validateProxy(value);
		case 'headers': return crawler.validateHeaders(value);
		case 'parameters': return fuzzer.validateParameters(value);
		case 'body-template': return fuzzer.validateBodyTemplate(value);
		case 'username-length':
		case 'password-length': return credGen.validateLength(value);
		default: return { error: false, message: '' };
	}
}
