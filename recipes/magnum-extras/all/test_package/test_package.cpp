#include <iostream>

#include "Magnum/Ui/Anchor.h"
#include "Magnum/Ui/BasicPlane.hpp"
#include "Magnum/Ui/BasicUserInterface.hpp"


struct UserInterface: Magnum::Ui::BasicUserInterface<> {
    using BasicUserInterface::BasicUserInterface;
};

struct Plane: Magnum::Ui::BasicPlane<> {
    using BasicPlane::BasicPlane;
};


int main() {
    std::cout << "magnum-extras\n";

    UserInterface ui{{800, 600}, {1600, 900}};
    Plane plane{ui, {Magnum::Ui::Snap::Left|Magnum::Ui::Snap::Top, {400.0f, 300.0f}}, {{10.0f, 25.0f}, {-15.0f, -5.0f}}, {7.0f, 3.0f}};

    auto padding = plane.padding();
    Magnum::Debug{&std::cout} << padding;
}
