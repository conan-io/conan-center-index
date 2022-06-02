#include "ThreadPool.hpp"

namespace sm
{
ThreadPool::~ThreadPool()
{
    wait_for_tasks();
    running = false;
    destroy_threads();
}

uint_fast64_t ThreadPool::get_tasks_queued() const
{
    const std::scoped_lock lock(queue_mutex);
    return tasks.size();
}

uint_fast32_t ThreadPool::get_tasks_running() const
{
    return tasks_total - /* (ui32) */ get_tasks_queued();
}

uint_fast32_t ThreadPool::get_tasks_total() const { return tasks_total; }

uint_fast32_t ThreadPool::get_thread_count() const { return thread_count; }

void ThreadPool::reset(const ui32& _thread_count)
{
    bool was_paused = paused;
    paused          = true;
    wait_for_tasks();
    running = false;
    destroy_threads();
    thread_count = _thread_count ? _thread_count : std::thread::hardware_concurrency();
    threads.reset(new std::thread[thread_count]);
    paused  = was_paused;
    running = true;
    create_threads();
}

void ThreadPool::wait_for_tasks()
{
    while (true)
    {
        if (!paused)
        {
            if (tasks_total == 0) break;
        }
        else
        {
            if (get_tasks_running() == 0) break;
        }
        sleep_or_yield();
    }
}
} // namespace sm
