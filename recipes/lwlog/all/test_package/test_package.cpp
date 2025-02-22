#include "lwlog.h"

int main()
{
    using logger_config = lwlog::configuration<
        lwlog::disable_local_time,
        lwlog::disable_thread_id,
        lwlog::disable_process_id,
        lwlog::disable_topics>;

    auto console = std::make_shared<
        lwlog::logger<
            logger_config,
            lwlog::asynchronous_policy<
                lwlog::default_async_queue_size,
                lwlog::default_overflow_policy>,
            lwlog::immediate_flush_policy,
            lwlog::single_threaded_policy,
            lwlog::sinks::stdout_sink>>("CONSOLE");

    console->set_level_filter(lwlog::level::info | lwlog::level::debug | lwlog::level::critical);
    console->set_pattern(".red([%T] [%n]) .dark_green([%l]): .cyan(%v) TEXT");

    console->critical("First critical message");

    return 0;
}
