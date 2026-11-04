#ifdef THREADPOOL_LESS_2_1_0
#include <ThreadPool/ThreadPool.h>
#else
#include <Leopard/ThreadPool.h>
#endif

#include <cassert>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <numeric>
#include <string>
#include <vector>

using namespace hmthrp;

// ----------------------------------------------------------------------------

static constexpr std::size_t    THREAD_COUNT = 5;

// ----------------------------------------------------------------------------

static void parallel_accumulate()  {

    std::cout << "Running parallel_accumulate() ..." << std::endl;

    constexpr std::size_t       n { 10003 };
    constexpr std::size_t       the_sum { (n * (n + 1)) / 2 };
    std::vector<std::size_t>    vec (n);

    std::iota(vec.begin(), vec.end(), 1);

    constexpr std::size_t                   block_size { n / THREAD_COUNT };
    std::vector<std::future<std::size_t>>   futs;
    auto                                    block_start = vec.begin();
    ThreadPool                              thr_pool { THREAD_COUNT };

    futs.reserve(THREAD_COUNT - 1);
    for (std::size_t i = 0; i < (THREAD_COUNT - 1); ++i)  {
        const auto  block_end { block_start + block_size };

        futs.push_back(
            thr_pool.dispatch(
                false,
                std::accumulate<decltype(block_start), std::size_t>,
                block_start, block_end, 0));
        block_start = block_end;
    }

    // Last result
    //
    std::size_t result { std::accumulate(block_start, vec.end(), 0UL) };

    for (std::size_t i = 0; i < futs.size(); ++i)
        result += futs[i].get();

    assert(result == the_sum);
    return;
}

// ----------------------------------------------------------------------------

int main (int, char *[])  {

    parallel_accumulate();

    return (EXIT_SUCCESS);
}
