#include "ironpress.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
    static const char source[] = "<h1>Installed with Conan</h1>";
    const IronpressBytes html = {(const uint8_t *)source, sizeof(source) - 1};
    IronpressBuffer *pdf = NULL;
    IronpressError *error = NULL;

    if (ironpress_html_to_pdf(html, &pdf, &error) != IRONPRESS_STATUS_OK) {
        ironpress_error_free(&error);
        return EXIT_FAILURE;
    }
    const int valid = ironpress_buffer_len(pdf) >= 4 &&
                      memcmp(ironpress_buffer_data(pdf), "%PDF", 4) == 0;
    ironpress_buffer_free(&pdf);
    return valid ? EXIT_SUCCESS : EXIT_FAILURE;
}
