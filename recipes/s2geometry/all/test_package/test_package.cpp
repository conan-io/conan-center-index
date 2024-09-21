#include <s2/s2builder.h>
#include <s2/s2builderutil_s2polygon_layer.h>
#include <s2/s2polygon.h>
#include <s2/s2text_format.h>

#include <iostream>
#include <memory>

int main()
{
   S2Builder builder{S2Builder::Options()};
   S2Polygon output;
   builder.StartLayer(std::make_unique<s2builderutil::S2PolygonLayer>(&output));
   auto input = s2textformat::MakePolygonOrDie("0:0, 0:5, 5:5, 5:0; 1:1, 1:4, 4:4, 4:1");
   builder.AddShape(*input->index().shape(0));
   S2Error error;
   std::cout << "Builder: " << (builder.Build(&error) ? "OK" : error.text()) << std::endl;
}
