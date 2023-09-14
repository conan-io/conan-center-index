#include "asyncly/executor/AsioExecutorController.h"
#include "asyncly/executor/MetricsWrapper.h"
#include "asyncly/executor/ThreadPoolExecutorController.h"

static void task()
{
}

int main()
{
    auto threadPool = asyncly::ThreadPoolExecutorController::create(2);

    threadPool->get_executor()->post([]() { task(); });

    return 0;
}
