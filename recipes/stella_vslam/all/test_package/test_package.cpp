#include <stella_vslam/util/converter.h>

using namespace stella_vslam;

int main() {
    util::converter::to_rot_mat(97.37 * M_PI / 180 * Vec3_t{9.0, -8.5, 1.1}.normalized());
}
