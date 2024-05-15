#include "thorvg.h"

int main() {
    const int WIDTH = 800;
    const int HEIGHT = 600;

    tvg::Initializer::init(tvg::CanvasEngine::Sw, 0);

    static uint32_t buffer[WIDTH * HEIGHT];  // canvas target buffer

    auto canvas = tvg::SwCanvas::gen();                                     // generate a canvas
    canvas->target(buffer, WIDTH, WIDTH, HEIGHT, tvg::SwCanvas::ARGB8888);  // buffer, stride, w, h, Colorspace

    auto rect = tvg::Shape::gen();               // generate a shape
    rect->appendRect(50, 50, 200, 200, 20, 20);  // define it as a rounded rectangle (x, y, w, h, rx, ry)
    rect->fill(100, 100, 100, 255);              // set its color (r, g, b, a)
    canvas->push(move(rect));                    // push the rectangle into the canvas

    auto circle = tvg::Shape::gen();           // generate a shape
    circle->appendCircle(400, 400, 100, 100);  // define it as a circle (cx, cy, rx, ry)

    auto fill = tvg::RadialGradient::gen();  // generate a radial gradient
    fill->radial(400, 400, 150);             // set the radial gradient geometry info (cx, cy, radius)

    tvg::Fill::ColorStop colorStops[2];         // gradient colors
    colorStops[0] = {0.0, 255, 255, 255, 255};  // 1st color values (offset, r, g, b, a)
    colorStops[1] = {1.0, 0, 0, 0, 255};        // 2nd color values (offset, r, g, b, a)
    fill->colorStops(colorStops, 2);            // set the gradient colors info

    circle->fill(move(fill));    // set the circle fill
    canvas->push(move(circle));  // push the circle into the canvas
}
