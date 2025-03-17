#include <PoseLib/poselib.h>

#include <vector>

int main() {
    std::vector<Eigen::Vector3d> x1(10, Eigen::Vector3d{});
    std::vector<Eigen::Vector3d> x2(10, Eigen::Vector3d{});
    Eigen::Matrix3d h;
    int res = poselib::homography_4pt(x1, x2, &h);
}
