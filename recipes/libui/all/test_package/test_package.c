#include "ui.h"
#include <stdio.h>

int main(void)
{
	uiInitOptions o;

	const char *err;
	o.Size = 0;
	err = uiInit(&o);
	if (err != NULL)
	{
		fprintf(stderr, "error initializing ui: %s\n", err);
		uiFreeInitError(err);
		return 0;
	}

	uiMain();
	uiUninit();
	return 0;
}
