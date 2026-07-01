#include "ThorSerialize/JsonThor.h"
#include "ThorSerialize/Traits.h"
#include <iostream>
#include <sstream>

struct Point {
    int x;
    int y;
};
ThorsAnvil_MakeTrait(Point, x, y);

int main() {
    Point p{3, 4};
    std::stringstream ss;
    ss << ThorsAnvil::Serialize::jsonExporter(p);
    std::cout << ss.str() << std::endl;
    return 0;
}
