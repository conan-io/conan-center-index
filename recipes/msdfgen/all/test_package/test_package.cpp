#include <msdfgen.h>
#include <msdfgen-ext.h>

#include <iostream>

int main(int argc, char **argv) {
    if (argc < 2) {
        std::cerr << "Need at least one argument\n";
        return 1;
    }

    msdfgen::FreetypeHandle *ft = msdfgen::initializeFreetype();
    if (ft) {
        msdfgen::FontHandle *font = msdfgen::loadFont(ft, argv[1]);
        if (font) {
            msdfgen::Shape shape;
            if (msdfgen::loadGlyph(shape, font, 'A')) {
                shape.normalize();
                msdfgen::edgeColoringSimple(shape, 3.0);
                msdfgen::Bitmap<float, 3> msdf(32, 32);
                msdfgen::generateMSDF(msdf, shape, 4.0, 1.0, msdfgen::Vector2(4.0, 4.0));
                msdfgen::savePng(msdf, "output.png");
            }
            msdfgen::destroyFont(font);
        }
        msdfgen::deinitializeFreetype(ft);
    }
    return 0;
}
