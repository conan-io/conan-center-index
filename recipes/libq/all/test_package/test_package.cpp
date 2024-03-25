#include <cstdlib>
#include <q/lib.hpp>
#include <q/blocking_dispatcher.hpp>
#include <q/execution_context.hpp>
#include <q/promise.hpp>

int main(void) {
    q::initialize();

    auto ctx = q::make_execution_context<q::blocking_dispatcher>("test");
    ctx->dispatcher()->start();
    ctx->dispatcher()->terminate(q::termination::annihilate);
    ctx->dispatcher()->await_termination();

    q::uninitialize();
    return EXIT_SUCCESS;
}
