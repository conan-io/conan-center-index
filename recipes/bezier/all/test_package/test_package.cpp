#include <iostream>
#include "bezier/bezier.h"

int main(void) {
    bezier::Bezier<3> cubicBezier({ {120, 160}, {35, 200}, {220, 260}, {220, 40} });

    bezier::Point p = cubicBezier.valueAt(0.5);
    std::cout << p.x << " " << p.y << std::endl;
}
