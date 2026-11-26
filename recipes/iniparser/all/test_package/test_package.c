#include <stdio.h>
#include <iniparser.h>

int main(void) {
    dictionary *ini = dictionary_new(0);
    iniparser_set(ini, "section:key", "value");
    printf("section:key = %s\n", iniparser_getstring(ini, "section:key", "missing"));
    iniparser_freedict(ini);
    return 0;
}
