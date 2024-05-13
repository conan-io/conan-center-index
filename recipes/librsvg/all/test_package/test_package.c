#include "zlib.h"
#include "glib-2.0/glib-object.h"
#include <librsvg/rsvg.h>

int main() {
    rsvg_set_default_dpi (72.0);
    return 0;
}