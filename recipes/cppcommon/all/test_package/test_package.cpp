#include "threads/thread.h"
#include "system/uuid.h"
#include "system/environment.h"
#include "time/timespan.h"
#include "system/dll.h"
#include "system/stack_trace.h"
#include "system/stack_trace_manager.h"

#include "interface/interface.h"

#include <sstream>
#include <locale>
#include <iostream>
#include <thread>

void function1()
{
    std::cout << "Thread Id: " << __THREAD__ << std::endl;
    std::cout << "Stack trace: " << std::endl << __STACK__ << std::endl;
}

void function2()
{
    function1();
}

void function3()
{
    function2();
}

int main()
{
    // Initialize stack trace manager of the current process
    CppCommon::StackTraceManager::Initialize();

    // Show the stack trace from the main thread
    function3();

    // Show the stack trace from the child thread
    std::thread(function3).join();

    // Cleanup stack trace manager of the current process
    CppCommon::StackTraceManager::Cleanup();

    CppCommon::Thread::Yield();
    CppCommon::UUID id;
    CppCommon::Timespan span;

    using namespace CppCommon;

    DLL plugin;
    std::cout << std::boolalpha << plugin.IsLoaded() << "\n";
    plugin.Load("plugin-function");
    std::cout << plugin.IsLoaded();
}
