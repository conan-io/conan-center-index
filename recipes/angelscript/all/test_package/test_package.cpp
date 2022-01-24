#include <angelscript.h>

#include <iostream>

int main()
{
    asIScriptEngine* const engine = asCreateScriptEngine();
    if (engine) {
        std::cerr << "successfully created engine" << std::endl;
        engine->ShutDownAndRelease();
        return 0;
    } else {
        std::cerr << "failed to create engine" << std::endl;
        return 1;
    }
}
