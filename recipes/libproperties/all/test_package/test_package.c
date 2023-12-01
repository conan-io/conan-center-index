#include "properties.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define LIBPROPERTIES_TEST_ASSERT(X) do {if(!(X))    {fprintf(stderr, "FAIL: %s\n", #X); abort();}} while(0)


int check_handler(void* context, char* key, int key_len, char* val, int val_len)
{
    LIBPROPERTIES_TEST_ASSERT(key_len == 3);
    LIBPROPERTIES_TEST_ASSERT(val_len == 3);
    LIBPROPERTIES_TEST_ASSERT(strncmp("aaa", key, 3) == 0);
    LIBPROPERTIES_TEST_ASSERT(strncmp("bbb", val, 3) == 0);
    return 0;
}


int main(int argc, char* argv[])
{
    char str[] = "aaa=bbb";
    struct properties_source_string_t source =
    {
        str,
        str + strlen(str)
    };
    properties_parse(&source, properties_source_string_read, NULL, check_handler);

    return 0;
}
