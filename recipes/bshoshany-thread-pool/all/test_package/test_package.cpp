#include "BS_thread_pool.hpp"

BS::synced_stream sync_out;
BS::thread_pool pool;

std::condition_variable ID_cv, total_cv;
std::mutex ID_mutex, total_mutex;
BS::concurrency_t count_unique_threads()
{
    const BS::concurrency_t num_tasks = pool.get_thread_count() * 2;
    std::vector<std::thread::id> thread_IDs(num_tasks);
    std::unique_lock<std::mutex> total_lock(total_mutex);
    BS::concurrency_t total_count = 0;
    bool ID_release = false;
    pool.wait_for_tasks();
    for (std::thread::id& id : thread_IDs)
        pool.push_task(
            [&total_count, &id, &ID_release]
            {
                id = std::this_thread::get_id();
                {
                    const std::scoped_lock total_lock_local(total_mutex);
                    ++total_count;
                }
                total_cv.notify_one();
                std::unique_lock<std::mutex> ID_lock_local(ID_mutex);
                ID_cv.wait(ID_lock_local, [&ID_release] { return ID_release; });
            });
    total_cv.wait(total_lock, [&total_count] { return total_count == pool.get_thread_count(); });
    {
        const std::scoped_lock ID_lock(ID_mutex);
        ID_release = true;
    }
    ID_cv.notify_all();
    total_cv.wait(total_lock, [&total_count, &num_tasks] { return total_count == num_tasks; });
    pool.wait_for_tasks();
    std::sort(thread_IDs.begin(), thread_IDs.end());
    return static_cast<BS::concurrency_t>(std::unique(thread_IDs.begin(), thread_IDs.end()) - thread_IDs.begin());
}

int main()
{
    const char* line = "------------------------------------------";
    sync_out.println(line);
    sync_out.println("Testing thread pool...");
    BS::concurrency_t unique_threads = count_unique_threads();
    if (pool.get_thread_count() == unique_threads)
    {
        sync_out.println("SUCCESS: Created ", unique_threads, " unique threads!");
        sync_out.println(line);
        return EXIT_SUCCESS;
    }
    else
    {
        sync_out.println("ERROR: Failed to create ", unique_threads, " unique threads!");
        sync_out.println(line);
        return EXIT_FAILURE;
    }
}
