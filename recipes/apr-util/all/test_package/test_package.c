#include "apr_uuid.h"
#include "apu_version.h"

#include <stdio.h>

int main() {
    apr_uuid_t uuid;
    char uuid_buffer[APR_UUID_FORMATTED_LENGTH+1];
    apr_uuid_get(&uuid);
    apr_uuid_format(uuid_buffer, &uuid);
    uuid_buffer[APR_UUID_FORMATTED_LENGTH] = '\0';
    printf("uuid: %s\n", uuid_buffer);

    printf("apr-util version %s\n", apu_version_string());

    return 0;
}
