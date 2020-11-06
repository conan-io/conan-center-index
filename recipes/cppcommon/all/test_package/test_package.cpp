#include "threads/thread.h"
#include "system/uuid.h"
#include "system/environment.h"
#include "time/timespan.h"
#include "system/dll.h"

// Plugins definitions
#include "interface/interface.h"

#include <sstream>
#include <locale>
#include <iostream>

int main()
{
    CppCommon::Thread::Yield();
    CppCommon::UUID id;
    CppCommon::Timespan span;

    using namespace CppCommon;

    DLL plugin;
    std::cout << std::boolalpha << plugin.IsLoaded() << "\n";
    plugin.Load("plugin-function");
    std::cout << plugin.IsLoaded();
}
