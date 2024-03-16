#include <stdio.h>
#include <string.h>
#include "evhtp/evhtp.h"
#include "evhtp/log.h"

static void
process_request_(evhtp_request_t * req, void * arg)
{
    (void)arg;

    evhtp_log_request_f(arg, req, stderr);
    evhtp_send_reply(req, EVHTP_RES_OK);
}

int
main(int argc, char ** argv)
{
    (void)argc;
    (void)argv;
    struct event_base * evbase;
    struct evhtp      * htp;
    void              * log;

    evbase = event_base_new();
    htp    = evhtp_new(evbase, NULL);
    log    = evhtp_log_new("$rhost $host '$ua' [$ts] '$meth $path HTTP/$proto' $status");

    evhtp_set_cb(htp, "/", process_request_, log);
    evhtp_enable_flag(htp, EVHTP_FLAG_ENABLE_ALL);
    return 0;
}
