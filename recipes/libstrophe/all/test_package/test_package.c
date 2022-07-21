#include <stdio.h>
#include <strophe.h>

int main()
{
    xmpp_ctx_t *ctx;
    char *uuid;
    int rc = 0;

    ctx = xmpp_ctx_new(NULL, NULL);

    uuid = xmpp_uuid_gen(ctx);
    if (uuid != NULL) {
        printf("%s\n", uuid);
        xmpp_free(ctx, uuid);
    } else {
        fprintf(stderr, "Couldn't allocate memory.\n");
        rc = 1;
    }

    xmpp_ctx_free(ctx);
    return rc;
}
