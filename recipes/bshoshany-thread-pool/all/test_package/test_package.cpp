#include "BS_thread_pool.hpp"

void store_ID(std::thread::id* location)
{
    *location = std::this_thread::get_id();
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
}

int main()
{
    BS::synced_stream sync_out;
    const char* line = "------------------------------------------";
    sync_out.println(line);
    sync_out.println("Testing thread pool...");
    BS::thread_pool pool;
    std::vector<std::thread::id> thread_IDs(pool.get_thread_count() * 4);
    BS::multi_future<void> futures;
    for (std::thread::id& id : thread_IDs)
        futures.f.push_back(pool.submit(store_ID, &id));
    futures.wait();
    std::sort(thread_IDs.begin(), thread_IDs.end());
    BS::concurrency_t unique_threads = (BS::concurrency_t)(std::unique(thread_IDs.begin(), thread_IDs.end()) - thread_IDs.begin());
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
