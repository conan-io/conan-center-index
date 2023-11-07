#include <stdio.h>
#include <stdlib.h>
#include <librsvg/rsvg.h>
#include <cairo.h>

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <input.svg> <output.png>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_svg = argv[1];
    const char *output_png = argv[2];

    // Load the SVG file
    GError *error = NULL;
    RsvgHandle *handle = rsvg_handle_new_from_file(input_svg, &error);
    if (error) {
        fprintf(stderr, "Error loading SVG: %s\n", error->message);
        return EXIT_FAILURE;
    }

    // Get dimensions of the SVG
    gdouble width, height;
    if (!rsvg_handle_get_intrinsic_size_in_pixels(handle, &width, &height)) {
        fprintf(stderr, "Error getting SVG dimensions.\n");
        return EXIT_FAILURE;
    }

    // Create a Cairo surface and context
    cairo_surface_t *surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, (int)width, (int)height);
    cairo_t *cr = cairo_create(surface);

    // Render the SVG onto the Cairo surface
    RsvgRectangle viewport = { 0, 0, width, height };
    if (!rsvg_handle_render_document(handle, cr, &viewport, &error)) {
        fprintf(stderr, "Error rendering SVG: %s\n", error->message);
        return EXIT_FAILURE;
    }

    // Write the result to a PNG file
    cairo_status_t status = cairo_surface_write_to_png(surface, output_png);
    if (status != CAIRO_STATUS_SUCCESS) {
        fprintf(stderr, "Failed to write to png: %s\n", cairo_status_to_string(status));
        return EXIT_FAILURE;
    }

    // Clean up
    cairo_destroy(cr);
    cairo_surface_destroy(surface);
    g_object_unref(handle);

    return EXIT_SUCCESS;
}
