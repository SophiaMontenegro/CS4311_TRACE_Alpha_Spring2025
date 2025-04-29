export async function load({ url }) {
	const formIndex = url.searchParams.get('formIndex');
	const noForm = url.searchParams.get('noForm') === 'true';

	return {
		formIndex: formIndex ? parseInt(formIndex) : 0,
		noForm
	};
}
