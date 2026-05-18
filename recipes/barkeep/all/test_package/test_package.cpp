#include <barkeep/barkeep.h>

int main(void) {
    barkeep::AnimationConfig cfg {};
    cfg.message = "Working";
    auto anim = barkeep::Animation(cfg);
    anim->done();

    return 0;
}
