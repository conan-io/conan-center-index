#include <iostream>

#include "libenvpp/env.hpp"

int main()
{
    auto pre = env::prefix("MYPROG");

    const auto num_threads_id = pre.register_required_variable<unsigned int>("NUM_THREADS");

    const auto parsed_and_validated_pre = pre.parse_and_validate();

    if (parsed_and_validated_pre.ok()) {
        const auto num_threads = parsed_and_validated_pre.get(num_threads_id);

        std::cout << "Num threads: " << num_threads << std::endl;
    } else {
        std::cout << parsed_and_validated_pre.warning_message();
        std::cout << parsed_and_validated_pre.error_message();
    }

    return 0;
}
