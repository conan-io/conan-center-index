#include <bx/math.h>

int main() {
    float tLerp = bx::lerp(0.0f, 10.0f, 0.5f);
    BX_TRACE("Lerped 0.0f to 10.0f at 0.5f, result %f", tLerp);
    BX_ASSERT(bx::isEqual(tLerp, 5.0f, 0.1f), "isEqual failed");
    return 0;
}
