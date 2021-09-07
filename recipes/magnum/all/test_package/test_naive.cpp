#include <iostream>
#include "Magnum/Math/Vector.h"
#include "Magnum/Math/StrictWeakOrdering.h"


int main() {
    const Magnum::Math::Vector<2, Magnum::Float> v2a{1.0f, 2.0f};
    const Magnum::Math::Vector<2, Magnum::Float> v2b{2.0f, 3.0f};
    const Magnum::Math::Vector<2, Magnum::Float> v2c{1.0f, 3.0f};

    Magnum::Math::StrictWeakOrdering o;
    if (o(v2a, v2b)) {
        std::cout << "Magnum working\n";
    }
}
