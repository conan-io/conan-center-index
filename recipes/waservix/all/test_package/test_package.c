#include <waservix/waservix.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    waservix_client *c = waservix_client_new("wpk_test");
    char *enc = waservix_url_encode("+250788123456");
    int ok = c != NULL && enc != NULL && strcmp(enc, "%2B250788123456") == 0 && waservix_verify_webhook("abc", "abc");
    printf("waservix %s: %s\n", WASERVIX_VERSION, ok ? "ok" : "failed");
    free(enc);
    waservix_client_free(c);
    return ok ? 0 : 1;
}
