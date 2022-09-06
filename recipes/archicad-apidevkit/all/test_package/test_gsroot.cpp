#include "Color.hpp"

int main() {
    Gfx::Color someColor;
    someColor.SetRed (176);

    assert (someColor.GetRed () == 176);
}
