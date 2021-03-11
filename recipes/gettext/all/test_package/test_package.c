#include <stdio.h>
#include <stdlib.h>

#include <libintl.h>
#include <locale.h>

#define _(STRING) gettext(STRING)

int main(int argc, char* argv[]) {
    const char* result = NULL;
    if (argc < 2) {
        printf("You must pass locale folder.\n");
        return EXIT_FAILURE;
    }

    result = setlocale(LC_MESSAGES,"");
    printf("LOCALE: %s\n", result);
    result = setlocale(LC_CTYPE,"");
    printf("LOCALE: %s\n", result);

    result = bindtextdomain("hello", argv[1]);
    printf("BIND TEXT DOMAIN: %s\n", result);

    result = textdomain("hello");
    printf("TEXT DOMAIN: %s\n", result);

    const char * lang = getenv("LANG");
    printf("'Hello World' in '%s': '%s'.\n", lang, _("Hello World"));

    return EXIT_SUCCESS;
}
