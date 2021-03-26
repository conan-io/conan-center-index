#include "stdlib.h"

#include "wslay/wslay.h"

int main()
{
    wslay_event_context_ptr ctx;
    const struct wslay_event_callbacks callbacks = { NULL };

    if(wslay_event_context_client_init(&ctx, &callbacks, NULL))
    {
        wslay_event_context_free(ctx);
    }

    return EXIT_SUCCESS;
}
