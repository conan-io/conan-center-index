#define CR_HOST
#include <cr.h>

void dummy() {
    cr_plugin ctx;
    cr_plugin_open(ctx, "xyz.dll");
    cr_plugin_update(ctx);
    cr_plugin_close(ctx);
}

int main() {}
