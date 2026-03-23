#include <cavc/polylineoffset.hpp>

#include <cassert>
#include <vector>

int main() {
    // Simple closed square polyline
    cavc::Polyline<double> input;
    input.addVertex(0, 0, 0);
    input.addVertex(10, 0, 0);
    input.addVertex(10, 10, 0);
    input.addVertex(0, 10, 0);
    input.isClosed() = true;

    // Offset inward by 1 unit — should produce a smaller square
    std::vector<cavc::Polyline<double>> results = cavc::parallelOffset(input, -1.0);
    assert(results.size() == 1);

    return 0;
}
