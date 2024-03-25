#include "ui.h"
#include <stdio.h>

void init_ui(void)
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
}

int main(void)
{
    // Do not actually create the UI in this test
    // init_ui();
	return 0;
}
