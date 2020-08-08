#include "OISInputManager.h"

using namespace OIS;

int main(int argc, char **argv)
{
    ParamList pl;
    InputManager* inputManager = InputManager::createInputSystem(pl);
    InputManager::destroyInputSystem(inputManager);
    return 0;
}
