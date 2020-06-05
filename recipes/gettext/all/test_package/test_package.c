#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <libintl.h>

int main(int argc, char * const argv[])
{
	if (argc < 2)
		return -1;
	if(!bindtextdomain("conan", argv[1]))
	{
		printf("Warning: Could not bind text domain\n");
	}
	if(!textdomain("conan"))
	{
		printf("Warning: Could not set text domain\n");
	}
	if(!setlocale(LC_ALL, ""))
	{
		printf("Warning: could not set locale\n");
	}
	const char * lang = getenv("LANG");
	lang = lang ? lang : "";
	printf("hello in %s: %s\n", lang, gettext("hello"));
    return 0;
}
