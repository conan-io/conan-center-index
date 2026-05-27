#include <cstdio>
#include <ruckig/ruckig.hpp>

int main() {
    using namespace ruckig;

    Ruckig<3> ruckig(0.01);
    InputParameter<3> input;
    OutputParameter<3> output;

    input.current_position = {0.0, 0.0, 0.0};
    input.current_velocity = {0.0, 0.0, 0.0};
    input.current_acceleration = {0.0, 0.0, 0.0};
    input.target_position = {1.0, 1.0, 1.0};
    input.target_velocity = {0.0, 0.0, 0.0};
    input.target_acceleration = {0.0, 0.0, 0.0};
    input.max_velocity = {1.0, 1.0, 1.0};
    input.max_acceleration = {1.0, 1.0, 1.0};
    input.max_jerk = {1.0, 1.0, 1.0};

    auto result = ruckig.update(input, output);
    printf("Ruckig update result: %d\n", static_cast<int>(result));
    return 0;
}
