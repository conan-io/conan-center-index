#define CI18N_IMPLEMENTATION
#include "ci18n.h"

#include <stdio.h>

int main(void)
{
    static const char ru[] = "files[one]={count} file\nfiles[few]={count} files, few\n";
    char text[64];

    ci18n_init();
    ci18n_load_from_buffer("ru", ru, sizeof(ru) - 1);
    ci18n_set_current("ru");
    ci18n_plural_copy("files", 3, text, sizeof(text));
    printf("ci18n %s: %s\n", CI18N_VERSION_STRING, text);
    ci18n_free();
    return 0;
}
