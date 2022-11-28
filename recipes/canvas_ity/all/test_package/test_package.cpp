#include <algorithm>
#include <fstream>

#define CANVAS_ITY_IMPLEMENTATION
#include "canvas_ity.hpp"

int main() {
    // Construct the canvas.
    static int const width = 256, height = 256;
    canvas_ity::canvas context( width, height );

    // Build a star path.
    context.move_to( 128.0f,  28.0f ); context.line_to( 157.0f,  87.0f );
    context.line_to( 223.0f,  97.0f ); context.line_to( 175.0f, 143.0f );
    context.line_to( 186.0f, 208.0f ); context.line_to( 128.0f, 178.0f );
    context.line_to(  69.0f, 208.0f ); context.line_to(  80.0f, 143.0f );
    context.line_to(  32.0f,  97.0f ); context.line_to(  98.0f,  87.0f );
    context.close_path();

    // Set up the drop shadow.
    context.set_shadow_blur( 8.0f );
    context.shadow_offset_y = 4.0f;
    context.set_shadow_color( 0.0f, 0.0f, 0.0f, 0.5f );

    // Fill the star with yellow.
    context.set_color( canvas_ity::fill_style, 1.0f, 0.9f, 0.2f, 1.0f );
    context.fill();

    // Draw the star with a thick red stroke and rounded points.
    context.line_join = canvas_ity::rounded;
    context.set_line_width( 12.0f );
    context.set_color( canvas_ity::stroke_style, 0.9f, 0.0f, 0.5f, 1.0f );
    context.stroke();

    // Draw the star again with a dashed thinner orange stroke.
    float segments[] = { 21.0f, 9.0f, 1.0f, 9.0f, 7.0f, 9.0f, 1.0f, 9.0f };
    context.set_line_dash( segments, 8 );
    context.line_dash_offset = 10.0f;
    context.line_cap = canvas_ity::circle;
    context.set_line_width( 6.0f );
    context.set_color( canvas_ity::stroke_style, 0.95f, 0.65f, 0.15f, 1.0f );
    context.stroke();

    // Turn off the drop shadow.
    context.set_shadow_color( 0.0f, 0.0f, 0.0f, 0.0f );

    // Add a shine layer over the star.
    context.set_linear_gradient( canvas_ity::fill_style, 64.0f, 0.0f, 192.0f, 256.0f );
    context.add_color_stop( canvas_ity::fill_style, 0.30f, 1.0f, 1.0f, 1.0f, 0.0f );
    context.add_color_stop( canvas_ity::fill_style, 0.35f, 1.0f, 1.0f, 1.0f, 0.8f );
    context.add_color_stop( canvas_ity::fill_style, 0.45f, 1.0f, 1.0f, 1.0f, 0.8f );
    context.add_color_stop( canvas_ity::fill_style, 0.50f, 1.0f, 1.0f, 1.0f, 0.0f );

    context.global_composite_operation = canvas_ity::source_atop;
    context.fill_rectangle( 0.0f, 0.0f, 256.0f, 256.0f );

    // Fetch the rendered RGBA pixels from the entire canvas.
    unsigned char *image = new unsigned char[ height * width * 4 ];
    context.get_image_data( image, width, height, width * 4, 0, 0 );
    // Write them out to a TGA image file (TGA uses BGRA order).
    unsigned char header[] = { 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        width & 255, width >> 8, height & 255, height >> 8, 32, 40 };
    for ( int pixel = 0; pixel < height * width; ++pixel )
        std::swap( image[ pixel * 4 + 0 ], image[ pixel * 4 + 2 ] );
    std::ofstream stream( "example.tga", std::ios::binary );
    stream.write( reinterpret_cast< char * >( header ), sizeof( header ) );
    stream.write( reinterpret_cast< char * >( image ), height * width * 4 );
    delete[] image;

    return 0;
}
