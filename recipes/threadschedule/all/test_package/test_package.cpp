#include <threadschedule/threadschedule.hpp>

int main()
{
    threadschedule::thread_pool pool(threadschedule::worker_count{1});
    auto result = pool.submit([] { return 42; });
    return result && result->get() == 42 ? 0 : 1;
}
