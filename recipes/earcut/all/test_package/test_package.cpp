#include <mapbox/earcut.hpp>

#include <array>
#include <vector>

/// The example below is taken directly from https://github.com/mapbox/earcut.hpp#usage.
int main(int, char **)
{
    // The number type to use for tessellation
    using Coord = double;

    // The index type. Defaults to uint32_t, but you can also pass uint16_t if you know that your
    // data won't have more than 65536 vertices.
    using N = uint32_t;

    // Create array
    using Point = std::array<Coord, 2>;
    std::vector<std::vector<Point>> polygon;

    // Fill polygon structure with actual data. Any winding order works.
    // The first polyline defines the main polygon.
    polygon.push_back({{100, 0}, {100, 100}, {0, 100}, {0, 0}});
    // Following polylines define holes.
    polygon.push_back({{75, 25}, {75, 75}, {25, 75}, {25, 25}});

    // Run tessellation
    // Returns array of indices that refer to the vertices of the input polygon.
    // e.g: the index 6 would refer to {25, 75} in this example.
    // Three subsequent indices form a triangle. Output triangles are clockwise.
    std::vector<N> indices = mapbox::earcut<N>(polygon);

    return indices.empty();
}
