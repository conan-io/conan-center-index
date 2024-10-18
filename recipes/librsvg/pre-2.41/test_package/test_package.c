#include <librsvg/rsvg.h>

int main() {
    GError *error = NULL;
    rsvg_handle_new_from_file("", &error);
}
