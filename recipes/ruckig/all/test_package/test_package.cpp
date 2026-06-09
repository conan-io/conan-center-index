#include <cstdio>
#include <ruckig/ruckig.hpp>

int main() {
    using namespace ruckig;

    Ruckig<1> ruckig(0.01);
    InputParameter<1> input;
    OutputParameter<1> output;

    input.target_position = {1.0};
    input.max_velocity = {1.0};
    input.max_acceleration = {1.0};
    input.max_jerk = {1.0};

    auto result = ruckig.update(input, output);
    printf("Ruckig update result: %d\n", static_cast<int>(result));
    return 0;
}
