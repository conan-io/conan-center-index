#include <cstdlib>
#include <q/lib.hpp>
#include <q/blocking_dispatcher.hpp>
#include <q/execution_context.hpp>
#include <q/promise.hpp>
#include <iostream>
#include <thread>

int main(void) {
    q::initialize();

    auto ctx = q::make_execution_context<q::blocking_dispatcher>("test");
    
    std::thread t([&ctx](){
        ctx->dispatcher()->start();
    });    
    std::this_thread::yield();    
    ctx->dispatcher()->terminate(q::termination::annihilate);
    ctx->dispatcher()->await_termination();
    t.join();

    q::uninitialize();
    return EXIT_SUCCESS;
}
