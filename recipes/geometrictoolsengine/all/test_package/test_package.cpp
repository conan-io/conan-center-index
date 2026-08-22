#include <Mathematics/AlignedBox.h>
#include <Mathematics/DistAlignedBoxAlignedBox.h>
#include <iostream>

#ifdef _WIN32
    #ifndef GTE_USE_MSWINDOWS
        #error "Missing GTE_USE_MSWINDOWS definition for Windows platform."
    #endif
#else
    #ifndef GTE_USE_LINUX
        #error "Missing GTE_USE_LINUX definition for Non-Windows platform."
    #endif
#endif

int main() {
    gte::AlignedBox3<double> box1({0.0, 0.0, 0.0}, {2.0, 2.0, 2.0});
    gte::AlignedBox3<double> box2({3.0, 0.0, 0.0}, {5.0, 5.0, 5.0});

    gte::DCPQuery<double, gte::AlignedBox3<double>, gte::AlignedBox3<double>> query;
    const double distance = query(box1, box2).distance;
    const double expectedDistance = 1.0;

    if (std::abs(distance - expectedDistance) > 1e-10) {
        std::cerr << "Error: expected " << expectedDistance << ", got " << distance << std::endl;
        return 1;
    }

    return 0;
}
