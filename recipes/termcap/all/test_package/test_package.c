#include <stdio.h>
#include <stdlib.h>
#include <termcap.h>


int main()
{
	char buf[1024] = {0};
	char *cl_string, *cm_string;
	int auto_wrap, height, width;

	tgetent(buf, getenv("TERM"));

	cl_string = tgetstr ("cl", NULL);
	cm_string = tgetstr ("cm", NULL);
	auto_wrap = tgetflag ("am");
	height = tgetnum ("li");
	width = tgetnum ("co");

	printf("cl: %s\n", cl_string);
	printf("cm: %s\n", cm_string);
	printf("am: %d\n", auto_wrap);
	printf("li: %d\n", height);
	printf("co: %d\n", width);

    return EXIT_SUCCESS;
}
