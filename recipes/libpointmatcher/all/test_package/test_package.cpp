#include <pointmatcher/PointMatcher.h>

int main()
{
    auto rigidTrans = PointMatcher<float>::get().REG(Transformation).create("RigidTransformation");
    return 0;
}
