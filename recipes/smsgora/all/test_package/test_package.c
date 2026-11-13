#include <smsgora/smsgora.h>

#include <stdio.h>
#include <string.h>

int main(void) {
    const char *body = "{\"event\":\"sms.received\"}";
    const char *sig = "sha256=313fe9b54923f49c8b94d50c5b96fa44f3f5a7ca90ef52fd55afb2bfd3ae8f60";
    smsgora_client *c = smsgora_client_new("sgk_test");
    int ok = c != NULL && smsgora_verify_webhook(body, strlen(body), sig, "whsec_test");
    printf("smsgora %s: %s\n", SMSGORA_VERSION, ok ? "ok" : "failed");
    smsgora_client_free(c);
    return ok ? 0 : 1;
}
