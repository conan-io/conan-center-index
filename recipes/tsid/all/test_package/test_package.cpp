#include <tsid/robots/robot-wrapper.hpp>
#include <pinocchio/multibody/model.hpp> 

using namespace tsid::robots;
using namespace pinocchio;

int main() {
    Model model;
    RobotWrapper robot(model);
    return 0;
}