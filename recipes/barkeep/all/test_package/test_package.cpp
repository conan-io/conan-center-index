#include <barkeep/barkeep.h>

int main(void) {
    auto anim = barkeep::Animation({.message = "Working"});
    anim->done();

    return 0;
}
