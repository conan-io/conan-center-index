#include "Color.hpp"
#include "assert.h"

int main () {
    Gfx::Color someColor;
    someColor.SetRed (176);

    assert (someColor.GetRed () == 176);
}
