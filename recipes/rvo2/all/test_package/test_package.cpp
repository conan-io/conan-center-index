#include <cstdlib>
#include <iostream>
#include <vector>

#include <RVO.h>

int main()
{
    RVO::RVOSimulator *sim = new RVO::RVOSimulator();

    sim->setTimeStep(0.25f);
    sim->setAgentDefaults(15.0f, 10, 5.0f, 5.0f, 2.0f, 2.0f);

    for (size_t i = 0; i < 5; ++i) {
		for (size_t j = 0; j < 5; ++j) {
			sim->addAgent(RVO::Vector2(55.0f + i * 10.0f,  55.0f + j * 10.0f));
			sim->addAgent(RVO::Vector2(-55.0f - i * 10.0f,  55.0f + j * 10.0f));
			sim->addAgent(RVO::Vector2(55.0f + i * 10.0f, -55.0f - j * 10.0f));
			sim->addAgent(RVO::Vector2(-55.0f - i * 10.0f, -55.0f - j * 10.0f));
		}
	}

    delete sim;
    return 0;
}
