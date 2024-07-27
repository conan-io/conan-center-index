#include <skia/core/SkPath.h>
#include <skia/core/SkPathBuilder.h>

int main() {
    SkPathBuilder pb;
    pb.moveTo(10, 10);
    pb.lineTo(15, 5);
    pb.lineTo(20, 10);
    pb.close();
    SkPath path1 = pb.detach();
}
