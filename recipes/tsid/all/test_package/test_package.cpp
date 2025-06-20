// Based on: https://github.com/stack-of-tasks/tsid/blob/master/tests/robot-wrapper.cpp

#include <iostream>

#include "tsid/robots/robot-wrapper.hpp"
#include <pinocchio/algorithm/joint-configuration.hpp>

using namespace std;
using namespace pinocchio;

using namespace tsid;
using namespace tsid::math;
using namespace tsid::robots;

int main(int argc, char *argv[]) {

    if (argc != 3) {
        cout << "Wrong args count" << endl;
        return 1;
    }

    const string test_model_path = argv[1];

    vector<string> package_dirs;
    package_dirs.push_back(test_model_path);
    string urdfFileName = package_dirs[0] + "/" + argv[2];

    RobotWrapper robot(urdfFileName, package_dirs,
                        pinocchio::JointModelFreeFlyer(), false);

    const Model& model = robot.model();

    // Update default config bounds to take into account the Free Flyer
    Vector lb(model.lowerPositionLimit);
    lb.head<3>().fill(-10.);
    lb.segment<4>(3).fill(-1.);

    Vector ub(model.upperPositionLimit);
    ub.head<3>().fill(10.);
    ub.segment<4>(3).fill(1.);

    Vector q = pinocchio::randomConfiguration(model, lb, ub);
    Vector v = Vector::Ones(robot.nv());
    Data data(robot.model());
    robot.computeAllTerms(data, q, v);

    Vector3 com = robot.com(data);
    std::cout << com << std::endl;

    std::cout << "robot.nq: "s << robot.nq() << std::endl;
    std::cout << "robot.nv: "s << robot.nv() << std::endl;

    return 0;
}
