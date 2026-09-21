#include <naxp/naxp.h>

#include <string.h>

uint64_t encode_with_c_interface(const char *pattern, const char *text)
{
	naxp *expression = naxp_parse(pattern, strlen(pattern), NULL);
	uint64_t value;

	if (expression == NULL)
	{
		return 0;
	}

	value = naxp_encode(expression, text, strlen(text));
	naxp_free(expression);

	return value;
}
