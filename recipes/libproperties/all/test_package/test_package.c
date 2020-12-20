#include <assert>

#include "properties.h"


#if ! defined(ASSERT)
#define ASSERT(x) assert(x)
#endif


int check_handler(void* context, char* key, int key_len, char* val, int val_len)
{
    ASSERT(key_len == 3);
    ASSERT(val_len == 3);
    ASSERT(strncmp("aaa", key, 3) == 0);
    ASSERT(strncmp("bbb", val, 3) == 0);
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
    properties_parse(&source, properties_source_string_read, NULL, test_handler);

    return 0;        
}
