#include <czmq.h>
int main (void)
{
    zsock_t *push = zsock_new_push ("inproc://example");
    zsock_t *pull = zsock_new_pull ("inproc://example");
    zstr_send (push, "Hello, World");

    char *string = zstr_recv (pull);
    puts (string);
    zstr_free (&string);

    zsock_destroy (&pull);
    zsock_destroy (&push);
    // https://github.com/zeromq/zproto/pull/384
#if defined (__WINDOWS__)
    zsys_shutdown();
#endif
    return 0;
}
